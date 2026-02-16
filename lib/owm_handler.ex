defmodule EXW.OWM_Handler do
  use GenServer
  require Logger
  require Req
  #require File

  #    File.write("test.txt", "#{counter}\n", [:append])
  #    data = Req.get!("https://duckduckgo.com")
  #    # IO.puts "data: #{inspect(data)}"
  #    IO.puts("data: #{data.status}")

  def start_link() do
    GenServer.start_link(__MODULE__, [], name: __MODULE__)
  end

  @impl true
  def init(_args) do
  	locations = EXW.get_locations()
	Logger.info "locations: #{inspect(locations)}"
	IO.puts "api key: #{EXW.get_api_key()}"
	{:ok, []}
  end

  # only one of the function heads has to be declared as a callback
  # the arguments are the message that was sent and the current state of the GenServer
  @impl true
  def handle_info(:tick, 0) do
  end

end
