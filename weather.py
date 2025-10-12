#!/bin/python3

#script for getting weather and forecast data 
#displaying it on a waveshare epaper display using a raspberrypi
#openweathermap token for API access needs to be placed in same directory as this file in a file named "openweathermap_token.txt"


import os, sys, time, jsonlines

# print help
if len(sys.argv) > 1:
    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print()
        print("weather info options:")
        print("  -h or --help to show this help dialog")
        print("  -t or --test for test mode without logging to file")
        print()
        exit()
    elif sys.argv[1] == "-t" or sys.argv[1] == "--test":
        print("[!] running in test mode without saving to log")
    else:
        print(f"ERROR unkown arguments {sys.argv[1:]} given")
        exit()


from lib import epd2in13_V2
from src import tools, gui

repo_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(repo_path)
sys.path.append(repo_path+"lib")
ressourcedir = "/home/pi/weather_info"
sys.path.append(ressourcedir)


def logging(town, currentData, forecastData):
    filename = f"weatherLog_{town}.jsonl"
    with jsonlines.open(filename, "a") as logFile:
        if time.localtime().tm_hour in [0,6,12,18]: 
            logFile.write(currentData)
            print(f"[!] logged current data to {filename}")
        if time.localtime().tm_hour == 0: #each day save the forecast once at midnight
            logFile.write(forecastData)
            print(f"[!] logged forecast data to {filename}")


def getOWMToken(): #openweathermap
    with open(ressourcedir+"/openweathermap_token.txt") as f:
        token = f.read().rstrip("\n")
    return token


def updateInfoFile(currentData):
    htmlContent = (f'<!DOCTYPE html>\n'
        '<html>\n'
        '<head>\n'
            '<title>Weather Info Status</title>\n'
        '</head>\n'
        '<body>\n'
            '<center>\n'
            '<h1>Weather Info Status</h1>\n'
            '<div style="background:#abcdef">\n'
                f'<p><span id="updateTime">{time.strftime("%d.%m.%y - %H:%M:%S")}</span>\n'
            '</div>\n'
            '<div style="background=#ffcdef">\n'
                '<img src="graphicalForecast.png" alt="graphical forecast" style="width:500px">\n'
            '</div>\n'
        '</body>\n'
        '</html>')
    fileName = "index.html"
    print(f"[!] writing to {fileName}")
    with open(fileName, "w") as f:
        f.write(htmlContent)


def main():
    testmode_flag = False

    if len(sys.argv) > 1 and (sys.argv[1] == "-t" or sys.argv[1] == "--test"):
        testmode_flag = True
        print(f"[!] test mode flag:{testmode_flag}")

    print("[#] Starting and configuring weather.py")

    token = getOWMToken()

    with open(ressourcedir+"/towns.txt") as f:
        towns = list(map(lambda t : t.rstrip('\n'), f.readlines()))
        displayTown = towns[0] #select town for which data is shown on screen

    print(f"[!] towns selected: {towns}")

    #try:
    print("[#] Starting and initialising e-paper module")
    global epd
    epd = epd2in13_V2.EPD()
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    print("[#] Starting program loop")
    while True: #loop that runs to update screen
        #epd.init(epd.FULL_UPDATE)

        for town in towns:
            print(f"[!] fetching data for {town}")
            currentDataRaw = tools.get_current_weather(token, town)
            print("[!] Received current weather")
            forecastDataRaw = tools.get_forecast(token, town)
            print("[!] Received forecast data")

            if testmode_flag:
                print("[!] test mode: no logging to file")
            else:
                logging(town, currentDataRaw,forecastDataRaw)

            if town != displayTown:
                continue

            print(f"[!] starting weather data display for {town}")
            epd.init(epd.FULL_UPDATE)
            print("[#] creating gui (epd.width:", epd.width, "epd.height:", epd.height, ")")
            #currentData: [temp,condition,wind_angle,wind_speed]
            currentData = tools.convertCurrentDisplayData(currentDataRaw)
            #forecastData (for each data point in the future): [z_string,z_float,t,s,c,r,p,h]
            forecastData = tools.convertForecastDisplayData(forecastDataRaw)
            image = gui.get_image(epd.width, epd.height, town, currentData, forecastData)
            print("[#] saving graphical forecast image")
            image.save("graphicalForecast.png", "PNG")
            print("[#] updating display")
            epd.display(epd.getbuffer(image))

        #except Exception as err:
        #    print(f"[!] ERROR: {err}")

        epd.sleep() #set epaper display to sleep mode

        print("[#] writing data to html file")
        updateInfoFile(currentData)

        if testmode_flag == True: #only run loop once when in test mode
            print("[!] Test Mode: SUCCESS, Exiting program")
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
