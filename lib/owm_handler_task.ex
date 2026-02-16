defmodule EXW.OWM_Handler_Task do
  require Logger
  require Req
  require File

  def hello() do
    Logger.info("OWM_Handler says Hello World")
    {:ok, data} = YamlElixir.read_from_file("config.yaml")
    IO.puts("locations from config.yaml: #{inspect(data["locations"])}")
  end

  def run(counter) do
    Logger.info("running... #{counter}")
    # File.write("test.txt", "#{counter}\n", [:append])
    # data = Req.get!("https://duckduckgo.com")
    # IO.puts "data: #{inspect(data)}"
    # IO.puts("data: #{data.status}")
    Process.sleep(100)
    if counter > 0, do: run(counter - 1), else: :ok
  end
end
