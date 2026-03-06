defmodule EXW do
  @moduledoc """
  Documentation for `EXW`.
  this is documentation, trust me
  """

  use Application
  require Logger

  # impl: this function is a callback
  @impl true
  def start(_type, _args) do
    log(:info, "STARTED")
    log(:debug, "Mix env: #{Mix.env()}")

    children = [
      {Registry, name: EXW, keys: :unique},
      %{id: :storage, start: {EXW.Storage, :start_link, [[name: :storage]]}},
	  %{id: :display, start: {EXW.Display, :start_link, [[name: :display]]}},
      {Task.Supervisor, name: EXW.OWM_Supervisor, strategy: :one_for_one},
      %{id: :controller, start: {EXW.Controller, :start_link, [[name: :controller]]}}
      # {DynamicSupervisor, name: EXW.OWM_Supervisor, strategy: :one_for_one},
      # Supervisor.child_spec({Task, fn -> EXW.OWM.test() end}, restart: :transient)
    ]

    res = Supervisor.start_link(children, strategy: :one_for_one)
    log(:info, "FINISHED START")
    res
    # Process.sleep(:infinity)
  end

  def log_msg(level, msg) do
    case level do
      :info -> Logger.info(msg)
      :debug -> Logger.debug(msg)
      :warning -> Logger.warning(msg)
      :error -> Logger.error(msg)
      _ -> :ok
    end
  end

  defp log(level, msg) do
    log_msg(level, "[#{__MODULE__}] " <> msg)
  end

  def read_api_key() do
    {:ok, key} = File.read("owm_token.txt")
    String.trim(key)
  end
end
