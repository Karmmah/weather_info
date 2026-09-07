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
		log(:debug, "starting")
		port =
			Port.open(
				#{:spawn, "python3 lib/info_server.py"},
				{:spawn, "python3 info_server.py"},
				#{:spawn, "python3 -m http.server 80"},
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
    #log(:info, "terminating info_server.py")
    #Port.command(port, "terminate\n")
    Port.close(port)
  end

  @impl true
  def handle_info(:update, port) do
  	log(:info, "updating index.html")
	File.write!("index.html",
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
				<p><span id="updateTime">the time is now</span>
			</div>
			<div style="background:#ffcdef">
				<img src="graphicalForecast.png" alt="graphical forecast" style="width:500px">
			</div>
		</body>
		</html>
		"""
	)
  	{:noreply, port}
  end

  def handle_info({_from_port, {:data, data}}, port) do
    log(:info, "info_server.py: #{inspect(data)}")
    {:noreply, port}
  end
end
