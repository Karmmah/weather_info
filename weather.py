#script for getting weather and forecast data and displaying it on a waveshare epaper display using a raspberrypi
#openweathermap token for API access needs to be placed in same directory as this file in a file named "openweathermap_token.txt"
import sys,os,time

libdir = '/home/pi/bcm2835-1.60/e-Paper/RaspberryPi_JetsonNano/python/lib' #for epd library
#ressourcedir = os.getcwd()
ressourcedir = "/home/pi/Desktop/weather_info"

sys.path.append(ressourcedir)
#picdir = '/home/pi/bcm2835-1.60/e-Paper/RaspberryPi_JetsonNano/python/pic' #for fonts
if os.path.exists(libdir):
	sys.path.append(libdir)
else:
	print('libdir path not found')

from waveshare_epd import epd2in13_V2

#data structures:
#current: [temp,condition,wind_angle,wind_speed]
#forecast (for each entry): [z_string,z_float,t,s,c,r,p,h]

def logging(current,forecast): #logging weather and forecast for later analysis of forecast accuracy
	with open("weather_log.txt","a") as log:
		if time.localtime().tm_hour in [0,6,12,18]: #four times a day save the current weather
			t = time.strftime('%Y.%m.%d-%H:%M:%S ')
			log.write("Current: "+t+str(int(time.time()))+" ")
			for item in current:
				print(item)
				log.write(str(item)+" ")
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
	logging(current,forecast)
	image = weather_gui.get_image(epd.width,epd.height,town,current,forecast)
	epd.display(epd.getbuffer(image))


def main():
	try:
		print("Starting weather.py")

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

		while True: #loop that runs to update screen each update interval
			epd.init(epd.FULL_UPDATE)
			update_screen(token,town)
			epd.sleep()
			print("Power saving mode (Ctrl+c to stop program)")
			time.sleep(update_interval)

	except IOError as e:
		print(e)
	except KeyboardInterrupt:
		print("\nProgram stopped")
		epd2in13_V2.epdconfig.module_exit()
		exit()
	except Exception as e:
		with open("errors.txt","a") as f:
			f.write("error:",e)
	finally:
		epd2in13_V2.epdconfig.module_exit()

if __name__ == "__main__":
	main()
