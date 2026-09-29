defmodule EXW.HTTPServer do
  use GenServer

  defp log(level, msg) do
    EXW.log_msg(level, "[#{__MODULE__}] " <> msg)
  end

  def start_link(opts) do
    GenServer.start_link(__MODULE__, [], opts)
  end

  @impl true
  def init(_args) do
    log(:info, "starting")

    port =
      Port.open(
        {:spawn, "python3 info_server.py"},
        [
          :binary,
          :exit_status,
          :use_stdio,
          :stderr_to_stdout
        ]
      )

    {:ok, port}
  end

  @impl true
  def terminate(_reason, port) do
    log(:warn, "terminating")
    log(:warn, "terminating info_server.py")
    # Port.command(port, "terminate\n")
    Port.close(port)
    log(:warn, "finished terminating")
  end

  @impl true
  def handle_info(:update, port) do
    log(:info, "updating index.html")

    File.write!(
      "index.html",
      """
      <!DOCTYPE html>
      <html>
      <head>
      	<title>Weather Info Status</title>
      </head>
      <body>
      	<center>
      	<h1>Weather Info Status</h1>
      	<div style="background:#abcdef">
      		<p><span id="updateTime">#{Calendar.strftime(DateTime.utc_now(), "%d.%m.%y - %H:%M:%S")} (UTC)</span>
      	</div>
      	<div style="background:#ffcdef">
      		<img src="graphicalForecast.png" alt="graphical forecast" style="width:500px">
      	</div>
      </body>
      </html>
      """
    )

    log(:debug, "finished")
    {:noreply, port}
  end

  def handle_info(:restart, port) do
    try do
      log(:debug, "stopping info_server.py")
      Port.command(port, "terminate\n")
      log(:debug, "terminated info_server.py")
      # check for successful termination
      log(:debug, "receiving confirmation")

      receive do
        {_from_port, {:data, data}} -> log(:info, "info_server.py: #{String.trim(data)}")
      end

      Port.close(port)
      log(:debug, "closed port")
    rescue
      err -> log(:error, "port error: #{inspect(err)}")
    end

    log(:debug, "starting new info_server.py")

    new_port =
      Port.open(
        {:spawn, "python3 info_server.py"},
        [
          :binary,
          :exit_status,
          :use_stdio,
          :stderr_to_stdout
        ]
      )

    log(:debug, "successfully started info_server.py")

    {:ok, new_port}
  end

  def handle_info({_from_port, {:data, data}}, port) do
    log(:info, "info_server.py: #{inspect(data)}")
    {:noreply, port}
  end
end
