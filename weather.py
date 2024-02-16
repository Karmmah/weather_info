#!/bin/python3

#script for getting weather and forecast data 
#displaying it on a waveshare epaper display using a raspberrypi
#openweathermap token for API access needs to be placed in same directory as this file in a file named "openweathermap_token.txt"


import sys, time

if len(sys.argv) > 1 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
	print("Launch options:")
	print("  -h or -help to show this help dialog")
	print("  -t or -test for test mode without logging to file")
	exit()

ressourcedir = "/home/pi/weather_info"

sys.path.append(ressourcedir)

import epd2in13_V2

#data structures:
#current: [temp,condition,wind_angle,wind_speed]
#forecast (for each entry): [z_string,z_float,t,s,c,r,p,h]


def logging(current,forecast):
	#logging weather and forecast for later analysis of forecast accuracy
	with open("weather_log.txt","a") as log:

		if time.localtime().tm_hour in [0,6,12,18]: 
			#four times a day save the current weather
			t = time.strftime('%Y.%m.%d-%H:%M:%S ')
			log.write("Current: " + t + str(int(time.time())) + " ")

			for item in current:
				print(item)
				log.write(str(item) + " ")
			log.write("\n")

		if time.localtime().tm_hour == 0: #each day save the forecast once
			log.write("Forecast: ")

			for item in forecast:
				log.write(item[1]+"-"+str(item[2])+"-"+str(item[3])+"-"+str(item[4])+"-"+str(item[5])+"-"+str(item[6])+"-"+str(item[7]))
				log.write(" ")
			log.write("\n")

import weather_tools,weather_gui



def main():
	if len(sys.argv) > 1 and\
			(sys.argv[1] == "-t" or sys.argv[1] == "--test"):
		print("Test Mode")

	print("Starting and configuring weather.py")
	update_interval = 3600 #seconds (once every hour)

	with open(ressourcedir+"/openweathermap_token.txt") as f:
		token = f.read().rstrip("\n")

	with open(ressourcedir+"/town.txt") as f:
		town = f.read().rstrip("\n")
	print("Selected Town: "+town)

	try:
		print("Starting and initialising e-paper module")
		global epd
		epd = epd2in13_V2.EPD()
		epd.init(epd.FULL_UPDATE)
		epd.Clear(0xFF)

		print("Starting program loop")
		last_update_time = 0
		while True: #loop that runs to update screen each update interval
			epd.init(epd.FULL_UPDATE)

			try:
				print("Received current weather")
				current = weather_tools.get_current_weather(token,town)
				print(f"len(current): {len(current)}")

				print("Received forecast data")
				forecast = weather_tools.get_forecast(token,town)
				print(f"len(forecast): {len(forecast)}")
			
				if len(sys.argv) > 1 and\
						(sys.argv[1] == "-t" or sys.argv[1] == "--"):
					print("test mode: no logging to file")
				else:
					logging(current,forecast)

				print("epd.width:", epd.width, "epd.height:", epd.height)
				image = weather_gui.get_image(\
					epd.width,epd.height,town,current,forecast)
				epd.display(epd.getbuffer(image))

			except Exception as err:
				print(f"ERROR: {err}")

			epd.sleep()
			last_update_time = time.time()
			print("Power saving mode (Ctrl+c to stop program)\n")

			while time.time() < last_update_time + update_interval:
				#seconds offset to compensate length of the update process
				time.sleep(60)

	except KeyboardInterrupt:
		print("\nProgram stopped")
		epd2in13_V2.epdconfig.module_exit()
		exit()

	except Exception as e:
		with open("errors.txt","a") as f:
			f.write(time.strftime('%Y.%m.%d-%H:%M:%S ')+"error:"+str(e))

	finally:
		epd2in13_V2.epdconfig.module_exit()


if __name__ == "__main__":
	main()

