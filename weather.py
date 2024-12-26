#!/bin/python3

#script for getting weather and forecast data 
#displaying it on a waveshare epaper display using a raspberrypi
#openweathermap token for API access needs to be placed in same directory as this file in a file named "openweathermap_token.txt"


import os, sys, time, jsonlines

if len(sys.argv) > 1 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
    print()
    print("Weather.py options:")
    print("  -h or --help to show this help dialog")
    print("  -t or --test for test mode without logging to file")
    print()
    exit()


from lib import epd2in13_V2
from src import tools, gui

repo_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(repo_path)
sys.path.append(repo_path+"lib")
ressourcedir = "/home/pi/weather_info"
sys.path.append(ressourcedir)

#data structures:
#current: [temp,condition,wind_angle,wind_speed]
#forecast (for each entry): [z_string,z_float,t,s,c,r,p,h]


def logging(current,forecast):
    #logging weather and forecast for later analysis of forecast accuracy
    #with open("weather_log.jsonl","a") as log:
    filename = "weatherLog.jsonl"
    with jsonlines.open(filename,"a") as writer:
        if time.localtime().tm_hour in [0,6,12,18]: 
            writer.write(current)
            print(f"[!] logged current data to {filename}")
        if time.localtime().tm_hour == 0: #each day save the forecast once
            writer.write(forecast)
            print(f"[!] logged forecast data to {filename}")
    #    if time.localtime().tm_hour in [0,6,12,18]: 
    #        #four times a day save the current weather
    #        t = time.strftime('%Y.%m.%d-%H:%M:%S ')
    #        writer.write("Current: " + t + str(int(time.time())) + " ")
    #        for item in current:
    #            print(item)
    #            writer.write(str(item) + " ")
    #        writer.write("\n")
    #    if time.localtime().tm_hour == 0: #each day save the forecast once
    #        writer.write("Forecast: ")
    #        for item in forecast:
    #            writer.write(item[1]+"-"+str(item[2])+"-"+str(item[3])+"-"+str(item[4])+"-"+str(item[5])+"-"+str(item[6])+"-"+str(item[7]))
    #            log.write(" ")
    #        writer.write("\n")


def getToken():
    with open(ressourcedir+"/openweathermap_token.txt") as f:
        token = f.read().rstrip("\n")
    return token


def main():
    testmode_flag = False

    if len(sys.argv) > 1 and (sys.argv[1] == "-t" or sys.argv[1] == "--test"):
        testmode_flag = True
        print("[!] Test Mode")

    print("[#] Starting and configuring weather.py")

    token = getToken()

    with open(ressourcedir+"/town.txt") as f:
        town = f.read().rstrip("\n")
    print("[!] Selected Town: "+town)

    #try:
    print("[#] Starting and initialising e-paper module")
    global epd
    epd = epd2in13_V2.EPD()
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    print("[#] Starting program loop")
    while True: #loop that runs to update screen
        epd.init(epd.FULL_UPDATE)

        #try:
        current = tools.get_current_weather(token,town)
        print("[!] Received current weather")
        forecast = tools.get_forecast(token,town)
        print("[!] Received forecast data")

        if testmode_flag:
            print("[!] test mode: no logging to file")
        else:
            logging(current,forecast)

        print("[#] creating gui (epd.width:", epd.width, "epd.height:", epd.height, ")")
        image = gui.get_image(epd.width,epd.height,town,
            tools.convertCurrentDisplayData(current),
            tools.convertForecastDisplayData(forecast),
            )
        print("[#] updating display")
        epd.display(epd.getbuffer(image))

        #except Exception as err:
        #    print(f"[!] ERROR: {err}")

        epd.sleep() #set epaper display to sleep mode

        if testmode_flag == True: #only run loop once when in test mode
            print("[!] Test Mode: Exiting program")
            epd2in13_V2.epdconfig.module_exit()
            exit()

        last_update_hour = time.strftime("%H")
        print("[!] Power saving mode (Ctrl+c to stop program)\n")
        while time.strftime("%H") == last_update_hour: #sleep several minute intervals until new hour
            time.sleep(2*60) #time in seconds

    #except KeyboardInterrupt:
    #    print("\n[!] Program stopped")
    #    epd2in13_V2.epdconfig.module_exit()
    #    exit()

    #except Exception as e:
    #    print(f"[!] ERROR: {e}")
    #    with open("errors.txt","a") as f:
    #        f.write(time.strftime('%Y.%m.%d-%H:%M:%S ')+"error:"+str(e)+"\n")

    #finally:
    #    print("[!] stopping main()")
    #    epd2in13_V2.epdconfig.module_exit()


if __name__ == "__main__":
    main()

