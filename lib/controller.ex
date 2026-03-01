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
      current_data: %{},
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
    now = DateTime.utc_now()

    log(
      :info,
      "Update started on #{Calendar.strftime(now, "%d.%m.%y")} at #{Calendar.strftime(now, "%H:%M:%S")}"
    )

    new_state =
      state
      |> update_current_weather_data()
      |> update_forecast_weather_data()
      |> Map.put(:last_update, DateTime.utc_now())

	# when starting up force the forecast data update
	new_state =
		case new_state.forecast_data do
			[] -> update_forecast_weather_data(new_state, :forced)
			_ -> new_state
		end

	log(:debug, "current data: #{inspect(new_state.current_data)}")
	log(:debug, "forecast data: #{inspect(new_state.forecast_data)}")

    send(self(), :sleep)
    {:noreply, new_state}
  end

  def handle_info(msg, state) do
    log(:error, "unknown message #{msg}")
    {:noreply, state}
  end

  defp update_current_weather_data(state) do
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

    send(:storage, {:update_current, current_data})
    Map.put(state, :current_data, current_data)
  end

  defp update_forecast_weather_data(state) do
    now = DateTime.utc_now()

    # update forecast at midnight
    case now.hour do
      0 -> update_forecast_weather_data(state, :forced)
      _ -> state
    end
  end

  defp update_forecast_weather_data(state, :forced) do
	tasks =
	  Enum.map(state.locations, fn loc ->
		Task.Supervisor.async_nolink(EXW.OWM_Supervisor, fn ->
		  EXW.OWM.fetch_forecast_weather_data(loc, state.key)
		end)
	  end)

	forecast_data =
	  Enum.reduce(tasks, [], fn task, acc ->
		case Task.await(task, 5000) do
		  {:ok, result} ->
			[result | acc]

		  {:exit, reason} ->
			log(:error, "Task failed #{inspect(reason)}")
			acc
		end
	  end)

	send(:storage, {:update_forecast, forecast_data})
	Map.put(state, :forecast_data, forecast_data)
  end
end
