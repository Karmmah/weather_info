defmodule EXW.Controller do
  use GenServer

  def start_link() do
    GenServer.start_link(__MODULE__, name: __MODULE__)
  end

  @impl true
  def init(_state) do
    IO.puts("TEST TEST TEST...")
    send(self(), :tick)

    state = %{
      key: EXW.read_api_key(),
      locations: EXW.read_locations()
    }

    {:ok, state}
  end

  @impl true
  def handle_info(:tick, state) do
    IO.puts("STIL TEST STIL TEST... state:#{inspect(state)}")
    # Process.sleep(next_hour - time)
    {:noreply, state}
  end

  def handle_info(msg, _state) do
  	Logger.error("[Controller] unkown message: #{msg}")
  end
end
