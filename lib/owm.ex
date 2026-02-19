defmodule EXW.OWM do
  use Task
  require Logger
  require Req

  defp log(level, msg) do
    EXW.log_msg(level, "[#{__MODULE__}] " <> msg)
  end

  def fetch_coordinates(city, api_key) do
    # OWM geocoding api call: http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&limit={limit}&appid={API key}
    # limit: how many results for the given city name should be shown, if there are multiple available
    log(:info, "calling OWM API to get coordinates for #{city}")
    url = "http://api.openweathermap.org/geo/1.0/direct?q=#{city}&limit=1&appid=#{api_key}"
    {:ok, data} = Req.get(url)
    city_info = Enum.at(data.body, 0)
    {:ok, [city_info["lat"], city_info["lon"]]}
    # [city_info["lat"], city_info["lon"]]
  end

  # def fetch_data(location, api_key) do
  #  %{name: name, lat: lat, lon: lon} = location
  #  excludes = "minutely,daily,alerts"
  #  url = "https://api.openweathermap.org/data/3.0/onecall?lat=#{lat}&lon=#{lon}&exclude=#{excludes}&appid=#{api_key}"
  #  {:ok, data} = Req.get(url)
  # end
end
