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
    Logger.debug("Mix env: #{Mix.env()}")

    children = [
      {Registry, name: EXW, keys: :unique},
      # %{id: :counter, start: {EXW.Counter, :start_link, [5]}, restart: :temporary},
      %{id: :owmhandler, start: {EXW.OWM_Handler, :start_link, []}, restart: :temporary},
      %{id: :controller, start: {EXW.Controller, :start_link, []}}
      # %{id: :test, start: {EXW, :test, []}}
    ]

    # res = Supervisor.start_link(children, strategy: :one_for_one, restart: :transient)
    res = Supervisor.start_link(children, strategy: :one_for_one)
    Logger.info(">> Supervisor start return value: #{inspect(res)}")
    Logger.info("finished EXW start")
    res
    # Process.sleep(:infinity)
  end

  def read_locations() do
    {:ok, data} = YamlElixir.read_from_file("config.yaml")
    data["locations"]
  end

  def read_api_key() do
    {:ok, key} = File.read("owm_token.txt")
    String.trim(key)
  end
end
