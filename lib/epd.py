#!/usr/bin/env python3

import os, json, sys
from PIL import Image,ImageDraw,ImageFont

#fontdir = '/home/pi/weather_info/lib'
#fontdir = '/lib'
fontdir = '/home/pk/code/weather_info/lib'
small_font = ImageFont.truetype(os.path.join(fontdir,'Font.ttc'),9)
text_font = ImageFont.truetype(os.path.join(fontdir,'Font.ttc'),20)
large_font = ImageFont.truetype(os.path.join(fontdir,'Font.ttc'),42)

def main():
    print("STARTED", flush=True)
    #inpt = input()
    #inpt = sys.stdin.readline()
    #print("hello world", flush=True)
    #while inpt != "terminate":
    for line in sys.stdin:
        print("loop", flush=True)
        #try:
        #    data = json.loads(cmd.strip())
        #    cmd = data["command"]
        #    if cmd != "display":
        #        print("ERROR: unknown command:", cmd, flush=True)
        #        continue
        #    current_data = data["current"]
        #    forecast_data = data["forecast"]
        #    print("SUCCESS: received current and forecast data", current_data, forecast_data, flush=True)
        #except:
        #    print("ERROR: input cannot be handled:", inpt, flush=True)
        #    continue
        #finally:
        #    inpt = input()
        #print(f"loop input: {inpt}", flush=True)
        #print("loop input:", inpt)
        #inpt = input()
        #inpt = sys.stdin.readline()
        line = line.strip()
        if not line: continue
        if line == "terminate":
            break
        try:
            data = json.loads(line)
            print(f"received data: {data}", flush=True)
        except:
            print("received invalid json data: {line}", flush=True)
    print("TERMINATED", flush=True)

if __name__ == "__main__":
    main()
