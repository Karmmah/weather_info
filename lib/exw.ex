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
    # Logger.info("[EXW] started")
    # Logger.debug("Mix env: #{Mix.env()}")
    log(:info, "started")
    log(:debug, "Mix env: #{Mix.env()}")

    children = [
      {Registry, name: EXW, keys: :unique},
      %{id: :controller, start: {EXW.Controller, :start_link, [[name: :controller]]}},
      {DynamicSupervisor, name: EXW.OWMSupervisor, strategy: :one_for_one}
      # %{id: :counter, start: {EXW.Counter, :start_link, [5]}, restart: :temporary},
      # Supervisor.child_spec({Task, fn -> EXW.OWM.test() end}, restart: :transient)
    ]

    # res = Supervisor.start_link(children, strategy: :one_for_one, restart: :transient)
    res = Supervisor.start_link(children, strategy: :one_for_one)
    log(:info, "finished start")
    res
    # Process.sleep(:infinity)
  end

  def log_msg(level, msg) do
    case level do
      :info -> Logger.info(msg)
      :debug -> Logger.debug(msg)
      :warning -> Logger.warning(msg)
      :error -> Logger.error(msg)
    end
  end

  defp log(level, msg) do
    log_msg(level, "[#{__MODULE__}] " <> msg)
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
