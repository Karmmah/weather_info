defmodule EXW.Counter do
  use GenServer
  require Logger

  def start_link(count) do
    GenServer.start_link(__MODULE__, count, name: __MODULE__)
  end

  @impl true
  def init(count) do
    Logger.info("Counter is initialised")
    send(self(), :tick)
    {:ok, count}
  end

  # only one of the function heads has to be declared as a callback
  # the arguments are the message that was sent and the current state of the GenServer
  @impl true
  def handle_info(:tick, 0) do
    Logger.info("counting: 0")
    Logger.warning("manually stopping the application with System.stop")
    # System.stop(status): stops the Erlang runtime asynchronously and carefully
    System.stop(0)
    Logger.debug("OWM_Handler returns {:stop, :normal, 0}")
    {:stop, :normal, 0}
  end

  def handle_info(:tick, count) when count > 0 do
    Logger.info("counting: #{count}")
    Process.send_after(self(), :tick, 300)
    {:noreply, count - 1}
  end

  def handle_info(msg, count) do
    Logger.warning("Unexpected message: #{inspect(msg)}")
    {:noreply, count}
  end
end
