defmodule EXW.OWM_Handler do
  use GenServer
  require Logger
  require Req

  def start_link() do
    GenServer.start_link(__MODULE__, [], name: __MODULE__)
  end

  def fetch_coordinates(city, api_key) do
    # OWM geocoding api call: http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&limit={limit}&appid={API key}
    # limit: how many results for the given city name should be shown, if there are multiple available
    Logger.info("calling OWM API to get coordinates for #{city}")
    url = "http://api.openweathermap.org/geo/1.0/direct?q=#{city}&limit=1&appid=#{api_key}"
    {:ok, data} = Req.get(url)
    city_info = Enum.at(data.body, 0)
    {:ok, [city_info["lat"], city_info["lon"]]}
  end

  @impl true
  def init(_args) do
    locations = EXW.read_locations()
    Logger.info("locations: #{inspect(locations)}")
    key = EXW.read_api_key()
    # IO.puts("api key: #{key}")

    city_name = "Berlin"

    [lat, lon] =
      case Mix.env() do
        :test ->
          Logger.debug("testing: skipping OWM API call to get coordinates for #{city_name}")
          [52.5170365, 13.3888599]

        _ ->
          {:ok, [lat, lon]} = fetch_coordinates(city_name, key)
          [lat, lon]
      end

    IO.puts("coordinates of Berlin: #{lat} #{lon}")
    {:ok, []}
  end

  # only one of the function heads has to be declared as a callback
  # the arguments are the message that was sent and the current state of the GenServer
  @impl true
  def handle_info(:tick, 0) do
  end
end
