#script providing functions for receiving weather and forecast data from openweathermap

import math,time,requests


def get_forecast(token,town):
	if not is_token_valid(token):
		print("Token is not valid")
		return []

	data_points = 40 #max = 5days * 8data points per day = 40
	url = "https://api.openweathermap.org/data/2.5/forecast?q=%s&%i&appid=%s"%(town,data_points,token)
	url_data = requests.get(url).json()
	
	gather_flag = True if time.localtime().tm_hour == 0 else False #gather/save forecast once per day to file at midnight
	forecast_data = []

	for i in range(len(url_data["list"])): #add required forecast data points to the array used to draw the graphs
		z_string = url_data['list'][i]['dt_txt'] #formatted time
		z_float = str(url_data['list'][i]['dt']) #unix time
		t = int(round(url_data['list'][i]['main']['temp']-273.15,0))
		s = round(url_data['list'][i]['wind']['speed'],1)
		c = url_data['list'][i]['clouds']['all'] #cloud cover percentage
		r = int(url_data['list'][i]['pop']*100) #probability of precipitation
		p = url_data['list'][i]['main']['pressure']
		h = url_data['list'][i]['main']['humidity']
		forecast_data += [[z_string,z_float,t,s,c,r,p,h]]

	return forecast_data


def get_current_weather(token,town):
	if not is_token_valid(token):
		print("Token is not valid")
		return []

	url = "https://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s"%(town,token)
	data = requests.get(url).json()
	
	temp = str(int(round(data['main']['temp']-273.15,0)))
	condition = str(data['weather'][0]['description'])
	wind_angle = round((float(data['wind']['deg'])/180.0)*math.pi-math.pi,2)
	wind_speed = str(m_s_to_beaufort(data['wind']['speed']))

	return [temp,condition,wind_angle,wind_speed]


def m_s_to_beaufort(speed):
	beaufort_scale = [0.5,1.5,3.3,5.5,7.9,10.7,13.8,17.1,20.7,24.4,28.4,32.6]
	for i in range(len(beaufort_scale)):
		if speed <= beaufort_scale[i]:
			return i
	return 12


def is_token_valid(token):
	if len(token) < 32 and len(token) > 20: #check length of token, 20 is arbitrary (could be higher or lower)
		return False
	else:
		return True


def test():
	town = "Aachen"
	with open("openweathermap_token.txt") as file:
		token = file.read().rstrip("\n")
	print("Current weather for "+town+": (temp,condition,wind angle,wind speed)\n")
	print(get_current_weather(token,town))

	data = get_forecast(token,town)
	forecast = ""
	for entry in data:
		forecast += entry[0]+","+str(entry[1])+","+str(entry[2])+","+str(entry[3])+","+str(entry[4])+","+str(entry[5])+","+str(entry[6])+","+str(entry[7])+"\n"
	print("Forecast for "+town+": (time1,time2,temp,wind speed,clouds,rain,pressure,humidity)")
	print(forecast)


if __name__ == "__main__":
	test()
