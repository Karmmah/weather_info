defmodule EXW.Controller do
  use GenServer
  require Logger

  defp log(level, msg) do
    EXW.log_msg(level, "[#{__MODULE__}] " <> msg)
  end

  def start_link(opts) do
    GenServer.start_link(__MODULE__, [], opts)
  end

  @impl true
  def init(_init_state) do
    log(:debug, "starting")

    api_key = EXW.read_api_key()
    log(:info, "openweathermap API key read")
    # TODO: add error handling when internet connection is not up
    locations = EXW.OWM.get_locations!(api_key)
    log(:info, "locations: #{inspect(locations)}")

    state = %{
      api_key: api_key,
      locations: locations,
      display_location: Enum.at(locations, 0),
      last_update: DateTime.utc_now()
    }

    send(:storage, {:fetch_data, locations, api_key})
    send(:display, :display)

    send(self(), :sleep)

    log(:debug, "FINISHED INIT")
    {:ok, state}
  end

  @impl true
  def handle_info(:update, state) do
    log(:info, "UPDATE STARTED")

    send(:storage, {:fetch_data, state.locations, state.api_key})
    send(:display, :display)

    state = Map.put(state, :last_update, DateTime.utc_now())

    send(self(), :sleep)
    log(:info, "UPDATE FINISHED")
    {:noreply, state}
  end

  def handle_info(:sleep, state) do
    # Sleep until next full hour since last update time
    # TODO: think about how this deals with summer/winter time so missing or doubled data might exist
    now = DateTime.utc_now()
    # remaining time until next hour in seconds
    rem_time = (60 - now.minute - 1) * 60 + (60 - now.second)

    log(:debug, "remaining seconds until next hour: #{rem_time}")

    sleep_time =
      case rem_time do
        rt when rem_time < 60 ->
          send(self(), :update)
          rt + 1

        rt ->
          send(self(), :sleep)
          rt - 59
      end

    log(:info, "sleeping for #{sleep_time} seconds")
    Process.sleep(sleep_time * 1000)
    log(:debug, "sleep finished")
    {:noreply, state}
  end

  def handle_info(msg, state) do
    log(:error, "unknown message #{msg}")
    {:noreply, state}
  end

end
