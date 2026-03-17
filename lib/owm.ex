defmodule EXW.OWM do
  use Task
  require Logger
  require Req

  defp log(level, msg) do
    EXW.log_msg(level, "[#{__MODULE__}] " <> msg)
  end

  @doc """
  	return locations with corresponding coordinates
  """
  def get_locations!(api_key) do
    # TODO:
    # - store fetched coordinates (in config?)
    # - fetch only if coordinates are not already stored
    data = YamlElixir.read_from_file!("config.yaml")
    # log(:debug, "read data: #{inspect(data)}")

    data["locations"]
    |> Enum.reduce(
      [],
      fn loc, acc ->
        # [lat, lon] = fetch_coordinates!(loc["name"], api_key)
        # [%{name: loc["name"], lat: lat, lon: lon} | acc]
        [lat, lon] = fetch_coordinates!(loc, api_key)
        [%{name: loc, lat: lat, lon: lon} | acc]
      end
    )
  end

  def fetch_coordinates!(city_name, api_key) do
    # TODO:
    # - what happens when city is not found?
    # OWM geocoding api call: http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&limit={limit}&appid={API key}
    # limit: how many results for the given city name should be shown, if there are multiple available
    log(:info, "calling OWM API to get coordinates for #{city_name}")
    url = "http://api.openweathermap.org/geo/1.0/direct?q=#{city_name}&limit=1&appid=#{api_key}"
    data = Req.get!(url)
    log(:info, "received coordinates (status #{data.status})")
    city_info = Enum.at(data.body, 0)
    [city_info["lat"], city_info["lon"]]
  end

  def fetch_current_weather_data(%{name: name, lat: lat, lon: lon}, api_key) do
    url = "https://api.openweathermap.org/data/2.5/weather?lat=#{lat}&lon=#{lon}&appid=#{api_key}"

    log(:info, "fetching current weather data for #{name}")

    case Req.get(url) do
      {:ok, raw_data} ->
        log(:info, "received current weather data for #{name} (status #{raw_data.status})")
        data = raw_data.body

        res = %{
          location: name,
          timestamp: data["dt"],
          cond: Enum.at(data["weather"], 0)["main"],
          cond_descr: Enum.at(data["weather"], 0)["description"],
          # temp: Float.round(data["main"]["temp"] - 273.15, 1),
          temp: data["main"]["temp"],
          hum: data["main"]["humidity"],
          cloud_cov: data["clouds"]["all"],
          rain: data["rain"]["1h"],
          pressure: data["main"]["pressure"],
          wind_dir: data["wind"]["deg"],
          wind_spd: data["wind"]["speed"],
          # wind_gust: data["wind"]["gust"],
          vis: data["visibility"]
        }

        {:ok, res}

      {:error, reason} ->
        # log(:error, "failed to fetch current weather data, because: #{reason}")
        {:error, "failed to fetch current weather data, because: #{reason}"}
    end
  end

  def fetch_forecast_weather_data(%{name: name, lat: lat, lon: lon}, api_key) do
    url =
      "https://api.openweathermap.org/data/2.5/forecast?lat=#{lat}&lon=#{lon}&appid=#{api_key}"

    log(:info, "fetching forecast weather data for #{name}")

    case Req.get(url) do
      {:ok, raw_data} ->
        log(:info, "received forecast weather data for #{name} (status #{raw_data.status})")
        data = raw_data.body

        res = %{
          location: name,
          forecast:
            Enum.map(data["list"], fn dp ->
              %{
                timestamp: dp["dt"],
                temp: Float.round(dp["main"]["temp"] - 273.15, 1),
                humidity: dp["main"]["humidity"],
                cloud_cov: dp["clouds"]["all"],
                rain_prob: dp["pop"],
                pressure: dp["main"]["pressure"],
                wind_dir: dp["wind"]["deg"],
                wind_spd: dp["wind"]["speed"],
                wind_gust: dp["wind"]["gust"],
                visibility: dp["visibility"]
              }
            end)
        }

        {:ok, res}

      {:error, reason} ->
        # log(:error, "failed to fetch forecast weather data, because: #{reason}")
        {:error, "failed to fetch forecast weather data, because: #{reason}"}
    end
  end

  # def fetch_pollution_data(%{name: _name, lat: lat, lon: lon},api_key) do
  # end
end
