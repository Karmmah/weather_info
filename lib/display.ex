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
		port = Port.open({:spawn, "python3 lib/epd.py"}, [:binary])
		{:ok, port}
	end

	@impl true
	def handle_info(:test, port) do
		# newline since pythons "input()" waits for \n to end the input
		send(port,{self(), {:command, "hello world\n"}})
		log(:info, "testing: sent hello world")
		receive do
			msg -> log(:info, "testing: received #{inspect(msg)}")
		end
		{:noreply, port}
	end

	def handle_info({_port, {:data, data}}, port) do
		log(:info, "testing: received data #{inspect(data)}")
		send(self(), :test)
		{:noreply, port}
	end
end
