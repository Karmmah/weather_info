#!/usr/bin/env python3

import os, json, sys, time, math, subprocess
from PIL import Image,ImageDraw,ImageFont

import epd2in13_V2

epd_width, epd_height, = 250, 122

fontdir = os.getcwd()+"/lib"
small_font = ImageFont.truetype(os.path.join(fontdir,'Font.ttc'),9)
text_font = ImageFont.truetype(os.path.join(fontdir,'Font.ttc'),20)
large_font = ImageFont.truetype(os.path.join(fontdir,'Font.ttc'),42)


#def get_image(data):
def get_image(epd_width, epd_height, location, current, forecast):
    image = Image.new('1',(epd_width,epd_height),255)
    draw = ImageDraw.Draw(image)

    # add town and time info 
    #time_str = time.strftime('%H:%M:%S')
    time_str = time.strftime('%H:%M')
    #w,h = draw.textsize(time_str, font=text_font)
    (left, top, right, bottom) = draw.textbbox((0,0), time_str, font=text_font)
    w, h = right - left, top - bottom
    draw.text((epd_width-w, epd_height-30), text=time_str, font=text_font)
    #w,h = draw.textsize(location)
    (left, top, right, bottom) = draw.textbbox((0,0), location)
    w, h = right - left, top - bottom
    draw.text((epd_width-w, epd_height-37), text=location)

    # add connection info
    try:
        #ip = subprocess.check_output("hostname -I", shell=True, text=True)
        #ip = ip.split(" ")[0]
        ip = subprocess.check_output(
            "ip a | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d'/' -f1",
            shell=True, text=True
        )
    except:
        ip = "No connection"
    draw.text((epd_width-84, epd_height-10), text=ip)
    print(f"connection info: {ip}", flush=True) #debug

    # big condition info
    temp = round(current["temp"] - 273.15) #[°C]
    temp_str = str(temp)
    #w,h = draw.textsize(temp,font=large_font)
    (left, top, right, bottom) = draw.textbbox((0,0), temp_str, font=large_font)
    w, h = right - left, top - bottom
    draw.text((237-w,2), text=temp_str, font=large_font, outline=0)
    draw.text((236,9), text='*C')
    draw.text((183,0), text=current["cond"], font=small_font) #condition

    # wind gauge
    radius = 20 #pixels
    center = (epd_width-radius-1, 64)
    angle, wind_speed = current["wind_dir"], round(current["wind_spd"])
    draw_windgauge(draw, center, radius, wind_speed, angle)

    # graphical forecast
    draw_graphical_forecast(epd_width, epd_height, draw, forecast)

    return image


def draw_windgauge(draw, center, radius, wind_spd, angle):
    wind_spd_str = str(wind_spd)
    #w, h = draw.textsize(wind_speed,font=text_font)
    (left, top, right, bottom) = draw.textbbox((0,0), wind_spd_str, font=text_font)
    w, h = right - left, top - bottom
    draw.ellipse((center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius), width=2)
    draw.line([center, (center[0]+radius*math.cos(angle), center[1]-radius*math.sin(angle))],  width=3)
    draw.line([center, (center[0]+radius*math.cos(angle-0.8*math.pi), center[1]-radius*math.sin(angle-0.8*math.pi))],  width=3)
    draw.line([center, (center[0]+radius*math.cos(angle+0.8*math.pi), center[1]-radius*math.sin(angle+0.8*math.pi))],  width=3)
    draw.ellipse((center[0]-radius/2, center[1]-radius/2, center[0]+radius/2, center[1]+radius/2), fill=0)
    #draw.text((center[0]-w/2+1,center[1]-h*0.6), text=wind_spd_str, font=text_font, fill=1, align='center')
    draw.text((center[0]-w/2+1, center[1]+h*1.0), text=wind_spd_str, font=text_font, fill=1, align='center')


def draw_graphical_forecast(epd_width, epd_height, draw, forecast):

    # unreasonable default values that get overwritten
    ranges = {
        "temp": [99.9, -99.9],
        "wind_spd": [999.9, -1.0],
        "cloud_cov": [101.0, -1.0],
        "rain_prob": [101.0, -1.0],
        "pressure": [9999.9, -1.0],
        "humidity": [101.0, -1.0]
    }

    for p in forecast:
        for k in ranges.keys():
            if p[k] < ranges[k][0]:
                ranges[k][0] = p[k]
            if p[k] > ranges[k][1]:
                ranges[k][1] = p[k]

    # always show certain values in range from 0-100; windspeed, clouds, rain, humidity
    #min_max[1],min_max[2],min_max[3],min_max[5] = [0,min_max[1][1]],[0,100],[0,100],[0,100]
    ranges["wind_spd"][0] = 0
    ranges["cloud_cov"][0], ranges["cloud_cov"][1] = 0, 100
    ranges["rain_prob"][0], ranges["rain_prob"][1] = 0, 100
    ranges["humidity"][0], ranges["humidity"][1] = 0, 100

    #start_label, end_label = forecast[0][0][:10], forecast[len(forecast)-1][0][:10] # time label
    #xborder_right = 108
    forecast_width = 141 #[px]

    #how many lines to draw; subtract two first entries which are just time and date
    data_lines_count = 6 #len(forecast[0])-2

    #width, height = (epd_height-xborder_right)/len(forecast), (epd_width-9)/data_lines_count
    width, height = forecast_width/len(forecast), (epd_height-9)/data_lines_count

    #draw border
    #draw.rectangle([(1,epd_height), (forecast_width, epd_height-height*data_lines_count)])
    draw.rectangle([(1, epd_height-height*data_lines_count), (forecast_width, epd_height)])

    ## draw vertical separators
    #for j in range(0, len(forecast)):
    #    if forecast[j][0][11:13] == "00":
    #        draw.line([(j*width, epd_height), (j*width, epd_height-height*data_lines_count)], width=1)

    #draw data lines
    curr_line = 0
    label_font = text_font
    #for i in range(data_lines_count):
    for k in ranges.keys():

        # horizontal line
        if curr_line != 0:
            draw.line([(0, epd_height-height*curr_line-1), (22, epd_height-height*curr_line-1)])
            draw.line([(forecast_width-37, epd_height-height*curr_line-1), (forecast_width, epd_height-height*curr_line-1)])

        y0 = epd_height + (curr_line + 1 - data_lines_count) * height
        #value = (float(forecast[0][i+2])-min_max[i][0]) / (min_max[i][1]-min_max[i][0]+0.001) #+0.001 to not divide by zero
        #y_left = y0 - height * value

        # draw entries
        polygon_points = [len(forecast)*width, y0, 0, y0] #add lower corners first
        for j in range(0,len(forecast)):
            #value = (float(forecast[j][i+2])-min_max[i][0])/(min_max[i][1]-min_max[i][0]+0.001) #+0.001 to not divide by zero
            value = (float(forecast[j][k])-ranges[k][0])/(ranges[k][1]-ranges[k][0]+.001) #+0.001 to not divide by zero
            x = j*width
            y = y0-height*value
            polygon_points += [x,y]

        # draw graph
        draw.polygon(polygon_points, fill=0)

        # draw lables for min and max values of each line
        #if i in [0,1,4]: #draw only selected min/max values
        #    draw.text((forecast_width+20,y0-height*0.5),text=str(min_max[i][0]))
        #    draw.text((forecast_width+20,y0-height*1.0+1),text=str(min_max[i][1]))
        draw.text((forecast_width+20, y0-height*0.5), text=str(ranges[k][0]))
        draw.text((forecast_width+20, y0-height*1.0+1), text=str(ranges[k][1]))

        #draw.text((forecast_width+3, epd_height-height*(1.5+curr_line)+6), text=k[0].upper(), font=label_font)
        draw.text((forecast_width+3, y0-21), text=k[0].upper(), font=label_font)

        curr_line += 1

    # time labels
    ##w,h = draw.textsize(end_label)
    #(left, top, right, bottom) = draw.textbbox((0,0), end_label)
    #w, h = right - left, top - bottom
    #draw.text((0, epd_height-height*data_lines_count-h), text=start_label)
    #draw.text((forecast_width-w, epd_height-height*data_lines_count-h), text=end_label)


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
            print(f"RECIEVED: command: {data["command"]}, current, forecast", flush=True)
        except:
            print("ERROR: received invalid json data: {line}", flush=True)
            continue

        epd.init(epd.FULL_UPDATE)
        #image = get_image({
        #    "width": epd.width,
        #    "height": epd.height,
        #    "location": current_data[0]["location"],
        #    "current": current,
        #    "forecast": forecast
        #})
        image = get_image(
            epd_width, epd_height,
            current_data[0]["location"], current_data[0], forecast_data[0]["forecast"]
        )
        #).rotate(-90, expand=True)
        epd.display(epd.getbuffer(image))
        image.save("graphicalForecast.png", "PNG")
        epd.sleep() #set epaper display to sleep mode

        print(f"SUCCESS", flush=True)

    epd2in13_V2.epdconfig.module_exit()
    print("TERMINATED", flush=True)

if __name__ == "__main__":
    main()
