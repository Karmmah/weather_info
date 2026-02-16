defmodule EXW do
  @moduledoc """
  Documentation for `EXW`.
  this is documentation, trust me
  """

  @doc """
  Hello world.

  ## Examples

      iex> EXW.hello()
      :world

  """
  def hello do
    :world
  end

  # ----------

  use Application
  require Logger

  # impl: this function is a callback
  @impl true
  def start(_type, _args) do
    Logger.info("EXW started")

    children = [
      {Registry, name: EXW, keys: :unique},
      # Supervisor.child_spec({Task, fn -> EXW.OWM_Handler_Task.hello() end}, id: :hello),
      # Supervisor.child_spec({Task, fn -> EXW.OWM_Handler_Task.run(3) end}, id: :owm_handler_task),
      # {EXW.OWM_Handler, 5}
      %{id: :counter, start: {EXW.Counter, :start_link, [5]}, restart: :temporary},
	  %{id: :owmhandler, start: {EXW.OWM_Handler, :start_link, []}, restart: :temporary}
    ]

    # res = Supervisor.start_link(children, strategy: :one_for_one, restart: :transient)
    res = Supervisor.start_link(children, strategy: :one_for_one)
    Logger.info(">> Supervisor start return value: #{inspect(res)}")
    Logger.info("finished EXW start")
    res
    # Process.sleep(:infinity)
  end

  def get_locations() do
      {:ok, data} = YamlElixir.read_from_file("config.yaml")
	  locations = data["locations"]
      #IO.puts("locations from config.yaml: #{inspect(locations)}")
	  locations
  end
end
