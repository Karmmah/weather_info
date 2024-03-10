#!/bin/python3

#script for getting weather and forecast data 
#displaying it on a waveshare epaper display using a raspberrypi
#openweathermap token for API access needs to be placed in same directory as this file in a file named "openweathermap_token.txt"


import os, sys, time

repo_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(repo_path)
sys.path.append(repo_path+"lib")

if len(sys.argv) > 1 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
	print("Launch options:")
	print("  -h or -help to show this help dialog")
	print("  -t or -test for test mode without logging to file")
	exit()

ressourcedir = "/home/pi/weather_info"

sys.path.append(ressourcedir)

from lib import epd2in13_V2

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

from src import tools, gui


def main():
	testmode_flag = False

	if len(sys.argv) > 1 and (sys.argv[1] == "-t" or sys.argv[1] == "--test"):
		testmode_flag = True
		print("Test Mode")

	print("Starting and configuring weather.py")

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
		while True: #loop that runs to update screen
			epd.init(epd.FULL_UPDATE)

			try:
				print("Received current weather")
				current = tools.get_current_weather(token,town)
				print(f"len(current): {len(current)}")

				print("Received forecast data")
				forecast = tools.get_forecast(token,town)
				print(f"len(forecast): {len(forecast)}")
			
				if testmode_flag:
					print("test mode: no logging to file")
				else:
					logging(current,forecast)

				print("creating gui (epd.width:", epd.width, "epd.height:", epd.height, ")")
				image = gui.get_image(epd.width,epd.height,town,current,forecast)

				print("updating display")
				epd.display(epd.getbuffer(image))

			except Exception as err:
				print(f"ERROR: {err}")

			epd.sleep()

			if testmode_flag == True:
				print("Test Mode: Exiting program")
				epd2in13_V2.epdconfig.module_exit()
				exit()

			last_update_hour = time.strftime("%H")
			print("Power saving mode (Ctrl+c to stop program)\n")
			while time.strftime("%H") == last_update_hour:
				time.sleep(60)

	except KeyboardInterrupt:
		print("\nProgram stopped")
		epd2in13_V2.epdconfig.module_exit()
		exit()

	except Exception as e:
		with open("errors.txt","a") as f:
			f.write(time.strftime('%Y.%m.%d-%H:%M:%S ')+"error:"+str(e)+"\n")

	finally:
		epd2in13_V2.epdconfig.module_exit()


if __name__ == "__main__":
	main()

