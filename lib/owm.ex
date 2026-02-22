defmodule EXW.OWM do
  use Task
  require Logger
  require Req

  defp log(level, msg) do
    EXW.log_msg(level, "[#{__MODULE__}] " <> msg)
  end

  def fetch_coordinates(city_name, api_key) do
    # TODO:
    # - what happens when city is not found?
    # OWM geocoding api call: http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&limit={limit}&appid={API key}
    # limit: how many results for the given city name should be shown, if there are multiple available
    log(:info, "calling OWM API to get coordinates for #{city_name}")
    url = "http://api.openweathermap.org/geo/1.0/direct?q=#{city_name}&limit=1&appid=#{api_key}"
    {:ok, data} = Req.get(url)
    log(:info, "received data with status #{data.status}")
    city_info = Enum.at(data.body, 0)
    [city_info["lat"], city_info["lon"]]
  end

  def fetch_current_weather_data(%{name: name, lat: lat, lon: lon}, api_key) do
    url = "https://api.openweathermap.org/data/2.5/weather?lat=#{lat}&lon=#{lon}&appid=#{api_key}"

    {:ok, data} = Req.get(url)
    # log(:debug,"#{inspect(data)}")
    res = %{
      location: name,
      timestamp: data.body["dt"],
      cond: Enum.at(data.body["weather"], 0)["main"],
      cond_descr: Enum.at(data.body["weather"], 0)["description"],
      temp: data.body["main"]["temp"],
      humidity: data.body["main"]["humidity"],
      cloud_cov: data.body["clouds"]["all"],
      rain: data.body["rain"]["1h"],
      pressure: data.body["main"]["pressure"],
      wind_dir: data.body["wind"]["deg"],
      wind_spd: data.body["wind"]["speed"],
      # wind_gust: data.body["wind"]["gust"],
      visibility: data.body["visibility"]
    }

    {:ok, res}
  end

  # def fetch_forecast_data(%{name: _name, lat: lat, lon: lon},api_key) do
  # end

  # def fetch_pollution_data(%{name: _name, lat: lat, lon: lon},api_key) do
  # end
end
