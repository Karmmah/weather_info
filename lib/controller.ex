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

    # TODO: remove weather data from state? it's already in storage
    state = %{
      key: api_key,
      locations: locations,
      last_update: DateTime.utc_now(),
      current_data: [],
      forecast_data: []
    }

    {current_data, forecast_data} = get_weather_data(state)
    log(:debug, "current data: #{inspect(current_data)}")
    log(:debug, "forecast data: #{inspect(forecast_data)}")

    state =
      state
      |> Map.put(:current_data, current_data)
      |> Map.put(:forecast_data, forecast_data)

    send(:storage, {:update_current, current_data})
    send(:storage, {:update_forecast, forecast_data})
    send(:display, {:display, current_data, forecast_data})

    send(self(), :sleep)

    log(:debug, "FINISHED INIT")
    {:ok, state}
  end

  @impl true
  def handle_info(:update, state) do
    log(:info, "UPDATE STARTED")

    state =
      state
      |> update_current_weather_data()
      |> update_forecast_weather_data()
      |> Map.put(:last_update, DateTime.utc_now())

    send(:display, {:display, "it's ya boi cwd", "ich bin fwd und ich bin auch dabei"})

    send(self(), :sleep)
    # log(:debug, "current data: #{inspect(state.current_data)}")
    # log(:debug, "forecast data: #{inspect(state.forecast_data)}")
    log(:info, "UPDATE FINISHED")
    {:noreply, state}
  end

  def handle_info(:sleep, state) do
    # Sleep until next full hour since last update time
    # TODO: think about how this deals with summer/winter time
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

    log(:debug, "sleeping for #{sleep_time} seconds")
    Process.sleep(sleep_time * 1000)
    log(:debug, "sleep finished")
    {:noreply, state}
  end

  def handle_info(msg, state) do
    log(:error, "unknown message #{msg}")
    {:noreply, state}
  end

  defp update_current_weather_data(state) do
    current_data = get_current_weather_data(state)
    send(:storage, {:update_current, current_data})
    Map.put(state, :current_data, current_data)
  end

  defp update_forecast_weather_data(state) do
    now = DateTime.utc_now()

    case now.hour do
      0 ->
        forecast_data = get_forecast_weather_data(state)
        send(:storage, {:update_forecast, forecast_data})
        Map.put(state, :forecast_data, forecast_data)

      _ ->
        state
    end
  end

  defp get_weather_data(state) do
    current_task =
      Task.Supervisor.async_nolink(EXW.OWM_Supervisor, fn ->
        EXW.Controller.get_current_weather_data(state)
      end)

    forecast_task =
      Task.Supervisor.async_nolink(EXW.OWM_Supervisor, fn ->
        EXW.Controller.get_forecast_weather_data(state)
      end)

    {Task.await(current_task, 5000), Task.await(forecast_task, 5000)}
  end

  @doc """
    helper function: get current weather data for all locations asynchronously and simultaneously
  """
  def get_current_weather_data(state) do
    tasks =
      Enum.map(state.locations, fn loc ->
        Task.Supervisor.async_nolink(EXW.OWM_Supervisor, fn ->
          EXW.OWM.fetch_current_weather_data(loc, state.key)
        end)
      end)

    Enum.reduce(tasks, [], fn task, acc ->
      case Task.await(task, 5000) do
        {:ok, result} ->
          [result | acc]

        {:exit, reason} ->
          log(:error, "Task failed #{inspect(reason)}")
          acc
      end
    end)
  end

  @doc """
    helper function: get forecast weather data for all locations asynchronously and simultaneously
  """
  def get_forecast_weather_data(state) do
    tasks =
      Enum.map(state.locations, fn loc ->
        Task.Supervisor.async_nolink(EXW.OWM_Supervisor, fn ->
          EXW.OWM.fetch_forecast_weather_data(loc, state.key)
        end)
      end)

    Enum.reduce(tasks, [], fn task, acc ->
      case Task.await(task, 5000) do
        {:ok, result} ->
          [result | acc]

        {:exit, reason} ->
          log(:error, "Task failed #{inspect(reason)}")
          acc
      end
    end)
  end
end
