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

    locations = EXW.get_locations(api_key)

    state = %{
      key: api_key,
      locations: locations,
      last_update: DateTime.utc_now(),
      current_data: [],
      forecast_data: []
    }

    # log(:debug, "state: #{inspect(state)}")

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

    # DynamicSupervisor.start_child(EXW.OWMSupervisor, {Task, fn location -> EXW.OWM.fetch_current_weather_data(location, state.key) end})
    # state.locations
    # |> Enum.reduce(
    # 	[],
    # 	fn loc, acc ->
    # 		DynamicSupervisor.start_child(EXW.OWMSupervisor, {Task, fn loc -> EXW.OWM.fetch_current_weather_data(loc, state.key))
    # 	end
    # 	)
    tasks =
      Enum.map(state.locations, fn loc ->
        Task.Supervisor.async_nolink(EXW.OWM_Supervisor, fn ->
          EXW.OWM.fetch_current_weather_data(loc, state.key)
        end)
      end)

    current_data =
      Enum.reduce(tasks, [], fn task, acc ->
        case Task.await(task, 5000) do
          {:ok, result} ->
            [result | acc]

          {:exit, reason} ->
            log(:error, "Task failed #{inspect(reason)}")
            acc
        end
      end)

    log(:debug, "current data: #{inspect(current_data)}")
	#send(:storage, {:update_current, current_data})

    new_state =
      Map.put(state, :last_update, DateTime.utc_now())
      |> Map.put(:current_data, current_data)

    send(self(), :sleep)
    {:noreply, new_state}
  end

  def handle_info(msg, state) do
    log(:error, "unknown message #{msg}")
    {:noreply, state}
  end
end
