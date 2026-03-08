defmodule EXW.Display do
  use GenServer

  defp log(level, msg) do
    EXW.log_msg(level, "[#{__MODULE__}] " <> msg)
  end

  def start_link(opts) do
    GenServer.start_link(__MODULE__, [], opts)
  end

  @impl true
  def init(_init_args) do
    log(:debug, "starting")

    port =
      Port.open({:spawn, "python3 lib/epd.py"}, [
        :binary,
        :exit_status,
        :use_stdio,
        :stderr_to_stdout
      ])

    {:ok, port}
  end

  @impl true
  def terminate(_reason, port) do
    log(:info, "terminating epd.py")
    # send(port, {:command, "terminate\n"})
    Port.command(port, "terminate\n")
    Port.close(port)
  end

  def handle_info({_port, {:exit_status, status}}, port) do
    log(:error, "epd.py exited with #{status}")
    {:stop, :port_terminated, port}
  end

  @impl true
  def handle_info({_from_port, {:data, data}}, port) do
    log(:info, "received data from epd.py #{inspect(data)}")
    {:noreply, port}
  end

  def handle_info({:display, current_data, forecast_data}, port) do
    log(:debug, "sending weather data to epd.py")

    data =
      Jason.encode!(%{
        command: :display,
        current: current_data,
        forecast: forecast_data
      })

    Port.command(port, data <> "\n")
    {:noreply, port}
  end
end
