defmodule EXW.Storage do
  use GenServer

  require Jason

  defp log(level, msg) do
    EXW.log_msg(level, "[#{__MODULE__}] " <> msg)
  end

  def start_link(opts) do
    GenServer.start_link(__MODULE__, [], opts)
  end

  @impl true
  def init(_init_state) do
    log(:debug, "starting")

    state = %{
      current_data: [],
      forecast_data: []
    }

    {:ok, state}
  end

  @impl true
  def handle_info({:update_current, new_current_data}, state) do
    log(:info, "updating current data with #{inspect(new_current_data)}")

    log(:debug, "current data: #{inspect(state.current_data)}")

    if state.current_data != [] do
      content =
        state.current_data
        # |> Jason.encode_to_iodata!()
        |> Jason.encode!()

      log(:debug, "saving current content #{inspect(content)}")
      File.write!("exw_log.jsonl", content <> "\n", [:append])
      # File.write!("exw_log.jsonl", content, [:append])
      # File.write!("exw_log.jsonl", "\n", [:append])
    end

    state = Map.put(state, :current_data, new_current_data)
    log(:debug, "finished")
    {:noreply, state}
  end

  def handle_info({:update_forecast, new_forecast_data}, state) do
    log(:info, "updating forecast data with #{inspect(new_forecast_data)}")

    if state.forecast_data != [] do
      content =
        state.forecast_data
        # |> Jason.encode_to_iodata!()
        |> Jason.encode!()

      log(:debug, "saving forecast content #{inspect(content)}")
      File.write!("exw_log.jsonl", content <> "\n", [:append])
      # File.write!("exw_log.jsonl", "\n", [:append])
      # File.write!("exw_log.jsonl", content, [:append])
    end

    state = Map.put(state, :forecast_data, new_forecast_data)
    log(:debug, "finished")
    {:noreply, state}
  end

  def handle_info(other, state) do
    log(:error, "unknown command given: #{inspect(other)}")
    {:noreply, state}
  end

  # terminate is called when the process is stopped externally
  # def terminate(_reason, state) do
  # end
end
