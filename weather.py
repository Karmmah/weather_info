#script for getting weather and forecast data and displaying it on a waveshare epaper display using a raspberrypi
#openweathermap token for API access needs to be placed in same directory as this file in a file named "openweathermap_token.txt"

import sys, time

ressourcedir = "/home/pi/weather_info"

sys.path.append(ressourcedir)

import epd2in13_V2

#data structures:
#current: [temp,condition,wind_angle,wind_speed]
#forecast (for each entry): [z_string,z_float,t,s,c,r,p,h]

def logging(current,forecast): #logging weather and forecast for later analysis of forecast accuracy
	with open("weather_log.txt","a") as log:

		if time.localtime().tm_hour in [0,6,12,18]: #four times a day save the current weather
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
def update_screen(token,town):
	global epd
	print("Town: "+town)
	current = weather_tools.get_current_weather(token,town)
	print("Received current weather")
	forecast = weather_tools.get_forecast(token,town)
	print("Received forecast data")

	if len(sys.argv) > 1 and (sys.argv[1] == "-t" or sys.argv[1] == "--test"):
		print("test, no logging to file")
	else:
		logging(current,forecast)

	image = weather_gui.get_image(epd.width,epd.height,town,current,forecast)
	epd.display(epd.getbuffer(image))


def print_help():
	print("Launch options:")
	print("  -h or -help to show this help dialog")
	print("  -t or -test for test mode without logging to file")

def main():
	if len(sys.argv)>1 and (sys.argv[1] == "-t" or sys.argv[1] == "--test"):
		print("Test Mode")

	try:
		print("Starting and configuring weather.py")
		with open(ressourcedir+"/update_interval.txt") as f:
			update_interval = int(f.read().rstrip("\n")) #seconds (once every hour)

		with open(ressourcedir+"/openweathermap_token.txt") as f:
			token = f.read().rstrip("\n")

		print("Starting and initialising e-paper module")
		global epd
		epd = epd2in13_V2.EPD()
		epd.init(epd.FULL_UPDATE)
		epd.Clear(0xFF)

		with open(ressourcedir+"/town.txt") as f:
			town = f.read().rstrip("\n")
		print("Selected Town: "+town)

		print("Starting program loop")
		while True: #loop that runs to update screen each update interval
			epd.init(epd.FULL_UPDATE)
			update_screen(token,town)
			epd.sleep()
			print("Power saving mode (Ctrl+c to stop program)\n")
			time.sleep(update_interval-6) #seconds offset to compensate length of the update process

	except IOError as e:
		print(e)
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
	if len(sys.argv) > 1 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
		print_help()
	else:
		main()
