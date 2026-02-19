defmodule EXW.Controller do
  use GenServer
  require Logger

  def start_link(opts) do
    GenServer.start_link(__MODULE__, [], opts)
  end

  defp log(level, msg) do
    EXW.log_msg(level, "[#{__MODULE__}] " <> msg)
  end

  @impl true
  def init(_init_state) do
    api_key = EXW.read_api_key()

    # TODO
    # store fetched coordinates
    # fetch only if coordinates are not already stored
    locations =
      EXW.read_locations()
      |> Enum.reduce(
        [],
        fn loc, acc ->
          {:ok, [lat, lon]} = EXW.OWM.fetch_coordinates(loc, api_key)
          [%{name: loc, lat: lat, lon: lon} | acc]
        end
      )

    state = %{
      key: api_key,
      locations: locations,
      last_update: DateTime.utc_now()
    }

    log(:debug, "state: #{inspect(state)}")

    # DynamicSupervisor.start_child(EXW.OWMSupervisor, {Task, fn -> EXW.OWM.test() end})

    send(self(), :update)

    log(:debug, "finished init")
    {:ok, state}
  end

  @doc """
  Sleep until next full hour since last update time
  """
  @impl true
  def handle_info(:sleep, state) do
    # TODO: think about how this deals with summer/winter time
    now = DateTime.utc_now()
    # remaining time until next hour in seconds
    rem_time = (60 - now.minute - 1) * 60 + (60 - now.second)

    log(:debug, "remaining seconds until next hour: #{rem_time}")

    sleep_time =
      case rem_time do
        rt when rem_time < 60 ->
          send(self(), :update)
		  log(:debug, "sending update message")
          rt + 1

        rt ->
          send(self(), :sleep)
          rt - 59
      end

    log(:debug, "sleeping for #{sleep_time} seconds")
    Process.sleep(sleep_time * 1000)
    log(:debug, "sleep finished")
    {:noreply, state}
  end

  def handle_info(:update, state) do
    log(:info, "This is an update...")
    send(self(), :sleep)
    {:noreply, state}
  end

  def handle_info(msg, state) do
    log(:error, "unknown message #{msg}")
    {:noreply, state}
  end
end
