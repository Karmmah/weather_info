defmodule EXW.Display do
  use GenServer

  # TODO:
  # - create system to display error messages on the display

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
    Port.command(port, "terminate\n")
    Port.close(port)
  end

  @impl true
  def handle_info(:restart, port) do
    try do
		Port.command(port, "terminate\n")

		receive do
		  {_from_port, {:data, data}} -> log(:info, "epd.py: #{String.trim(data)}")
		end

		Port.close(port)
	rescue
		err -> log(:warning, "port error: #{inspect(err)}")
	end

    port =
      Port.open({:spawn, "python3 lib/epd.py"}, [
        :binary,
        :exit_status,
        :use_stdio,
        :stderr_to_stdout
      ])

	send(self(), :display)

    {:noreply, port}
  end

  def handle_info({_port, {:exit_status, status}}, port) do
    log(:error, "epd.py exited with #{status}")
    {:stop, :port_terminated, port}
  end

  def handle_info(:display, port) do
	{current_data, forecast_data} = GenServer.call(:storage, :get_data)

    log(:info, "sending weather data to epd.py")
    data =
      Jason.encode!(%{
        command: :display,
        current: current_data,
        forecast: forecast_data
      }) <> "\n"

    Port.command(port, data)
    {:noreply, port}
  end

  def handle_info({_from_port, {:data, data}}, port) do
    log(:info, "epd.py: #{inspect(data)}")
    {:noreply, port}
  end
end
