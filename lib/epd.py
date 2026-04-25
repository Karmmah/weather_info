#!/usr/bin/env python3

import os, json, sys, time, math, subprocess, datetime
from PIL import Image,ImageDraw,ImageFont

import epd2in13_V2

epd_width, epd_height, = 250, 122

fontdir = os.getcwd()+"/lib"
small_font = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 9)
text_font = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 20)
large_font = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 42)


#def get_image(data):
def get_image(epd_width, epd_height, location, current, forecast):
    image = Image.new('1',(epd_width,epd_height),255)
    draw = ImageDraw.Draw(image)

    # add town and time info 
    time_str = time.strftime('%H:%M')
    (left, top, right, bottom) = draw.textbbox((0,0), time_str, font=text_font)
    w, h = right - left, top - bottom
    draw.text((epd_width-w, epd_height-30), text=time_str, font=text_font)
    (left, top, right, bottom) = draw.textbbox((0,0), location)
    w, h = right - left, top - bottom
    draw.text((epd_width-w, epd_height-37), text=location)

    # add connection info
    try:
        ip = subprocess.check_output(
            "ip a | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d'/' -f1",
            shell=True, text=True
        ).strip()
    except:
        ip = "No connection"
    draw.text((epd_width, epd_height-9), text=ip, anchor="rt")
    print(f"connection info: {ip}", flush=True) #debug

    # big condition info
    temp = round(current["temp"] - 273.15) #[°C]
    temp_str = str(temp)
    (left, top, right, bottom) = draw.textbbox((0,0), temp_str, font=large_font)
    w, h = right - left, top - bottom
    draw.text((237-w,2), text=temp_str, font=large_font, outline=0)
    draw.text((236,9), text='*C')
    draw.text((epd_width,0), text=current["cond"], font=small_font, anchor='rt')

    # wind gauge
    radius = 20 #pixels
    center = (epd_width-radius-1, 65)
    angle, wind_speed = current["wind_dir"], round(current["wind_spd"])
    draw_windgauge(draw, center, radius, wind_speed, angle)

    # graphical forecast
    draw_graphical_forecast(epd_width, epd_height, draw, forecast)

    return image


def draw_windgauge(draw, center, radius, wind_spd, angle):
    #wind_spd_str = str(wind_spd)
    wind_spd_str = str(round((wind_spd/0.836)**(2/3))) # beaufort scale
    (left, top, right, bottom) = draw.textbbox((0,0), wind_spd_str, font=text_font)
    w, h = right - left, top - bottom
    draw.ellipse((center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius), width=2)
    draw.line([center, (center[0]+radius*math.cos(angle), center[1]-radius*math.sin(angle))],  width=3)
    draw.line([center, (center[0]+radius*math.cos(angle-0.8*math.pi), center[1]-radius*math.sin(angle-0.8*math.pi))],  width=3)
    draw.line([center, (center[0]+radius*math.cos(angle+0.8*math.pi), center[1]-radius*math.sin(angle+0.8*math.pi))],  width=3)
    draw.ellipse((center[0]-radius/2, center[1]-radius/2, center[0]+radius/2, center[1]+radius/2), fill=0)
    draw.text((center[0]-w/2+0, center[1]+h*0.83), text=wind_spd_str, font=text_font, fill=1, align='center')


def draw_graphical_forecast(epd_width, epd_height, draw, forecast):
    forecast_x0 = 17
    forecast_width = 153 #[px]

    # unreasonable default values that get overwritten
    ranges = {
        "temp": [99.9, -99.9],
        "wind_spd": [999.9, -1.0],
        "cloud_cov": [101.0, -1.0],
        "rain_prob": [101.0, -1.0],
        "pressure": [9999.9, -1.0],
        "humidity": [101.0, -1.0]
    }

    # how many lines to draw; subtract two first entries which are just time and date
    data_lines_count = len(ranges)
    width, height = forecast_width/len(forecast), (epd_height-9)/data_lines_count

    # draw border
    draw.rectangle([(forecast_x0, epd_height-height*data_lines_count), (forecast_x0 + forecast_width, epd_height)])

    prev_hour = 0
    for i,p in enumerate(forecast):
        # draw vertical day separator lines
        curr_hour = datetime.datetime.fromtimestamp(p["timestamp"]).hour
        if curr_hour - prev_hour < 0: # mark beginning of new day
            draw.line([(forecast_x0+i*width, epd_height), (forecast_x0+i*width, epd_height-height*data_lines_count)], width=1)
        prev_hour = curr_hour
        # get min/max values
        for k in ranges.keys():
            if p[k] < ranges[k][0]:
                ranges[k][0] = p[k]
            if p[k] > ranges[k][1]:
                ranges[k][1] = p[k]

    # always show certain values in range from 0-100; windspeed, clouds, rain, humidity
    ranges["wind_spd"][0] = 0
    ranges["cloud_cov"][0], ranges["cloud_cov"][1] = 0, 100
    ranges["rain_prob"][0], ranges["rain_prob"][1] = 0, 100
    ranges["humidity"][0], ranges["humidity"][1] = 0, 100

    # draw data lines
    curr_line = 0
    for k in ranges.keys():

        # draw entries
        y0 = epd_height + (curr_line + 1 - data_lines_count) * height
        polygon_points = [forecast_x0+len(forecast)*width, y0, forecast_x0, y0] #add lower corners first
        for j in range(0,len(forecast)):
            value = (float(forecast[j][k])-ranges[k][0])/(ranges[k][1]-ranges[k][0]+.001) #+0.001 to not divide by zero
            x = forecast_x0 + j*width
            y = y0-height*value
            polygon_points += [x,y]

        # draw graph
        draw.polygon(polygon_points, fill=0)

        # draw label for what data is displayed in each line
        draw.text((9, y0-16), text=k[0].upper(), font=text_font, anchor="mt")

        # draw lables for min and max values of each line
        draw.text((forecast_width+20, y0-height*0.6), text=str(ranges[k][0]))
        draw.text((forecast_width+20, y0-height*1.1), text=str(ranges[k][1]))

        curr_line += 1

    # time labels
    start_label = str(datetime.datetime.fromtimestamp(forecast[0]['timestamp']).date())
    end_label = str(datetime.datetime.fromtimestamp(forecast[-1]['timestamp']).date())
    (left, top, right, bottom) = draw.textbbox((0,0), end_label)
    w, h = right - left, top - bottom
    draw.text((forecast_x0, 0), text=start_label, anchor='lt')
    draw.text((forecast_x0+forecast_width, 0), text=end_label, anchor='rt')


def main():
    print("STARTING", flush=True)

    epd = epd2in13_V2.EPD()
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    print("RECEIVING", flush=True)
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        if line == "terminate":
            break

        current_data, forecast_data = [], []
        try:
            data = json.loads(line)
            assert data["command"] == "display"
            current_data = data["current"]
            forecast_data = data["forecast"]
            print(f"RECIEVED: command: {data["command"]}, current: keys:{current_data[0].keys()}, forecast: len:{len(forecast_data[0]['forecast'])} keys:{forecast_data[0]['forecast'][0].keys()}", flush=True)
        except:
            print("ERROR: received invalid json data: {line}", flush=True)
            continue

        epd.init(epd.FULL_UPDATE)

        image = get_image(
            epd_width, epd_height,
            current_data[0]["location"], current_data[0], forecast_data[0]["forecast"]
        )
        epd.display(epd.getbuffer(image))
        #image.save("graphicalForecast.png", "PNG")

        epd.sleep() #set epaper display to sleep mode
        print(f"SUCCESS", flush=True)

    epd2in13_V2.epdconfig.module_exit()
    print("TERMINATED", flush=True)

if __name__ == "__main__":
    main()
