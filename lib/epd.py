#!/usr/bin/env python3

import os, json, sys, time, math
from PIL import Image,ImageDraw,ImageFont

import epd2in13_V2

epd_width, epd_height, = 250, 122

#fontdir = '/home/pi/weather_info/lib'
#fontdir = '/lib'
#fontdir = '/home/pk/code/weather_info/lib'
fontdir = os.getcwd()+"/lib"
small_font = ImageFont.truetype(os.path.join(fontdir,'Font.ttc'),9)
text_font = ImageFont.truetype(os.path.join(fontdir,'Font.ttc'),20)
large_font = ImageFont.truetype(os.path.join(fontdir,'Font.ttc'),42)


#def get_image(data):
def get_image(epd_width, epd_height, location, current, forecast):
    #epd_width = data["width"]
    #epd_height = data["height"]
    #location = data["location"]
    #current = data["current"]
    #forecast = data["forecast"]

    image = Image.new('1',(epd_height,epd_width),255)
    draw = ImageDraw.Draw(image)

    # add town and time info 
    #time_str = time.strftime('%H:%M:%S')
    time_str = time.strftime('%H:%M')
    #w,h = draw.textsize(time_str, font=text_font)
    (left, top, right, bottom) = draw.textbbox((0,0), time_str, font=text_font)
    w, h = right - left, top - bottom
    draw.text((epd_height-w, epd_width-30), text=time_str, font=text_font)
    #w,h = draw.textsize(location)
    (left, top, right, bottom) = draw.textbbox((0,0), location)
    w, h = right - left, top - bottom
    draw.text((epd_height-w, epd_width-37), text=location)

    # add connection info
    try:
        ip = subprocess.check_output("hostname -I", shell=True, text=True)
        ip = ip.split(" ")[0]
    except:
        ip = "No connection"
    draw.text((epd_height-84, epd_width-10), text = ip)

    # big condition info
    temp = current["temp"]
    temp_str = str(temp)
    #w,h = draw.textsize(temp,font=large_font)
    (left, top, right, bottom) = draw.textbbox((0,0), temp_str, font=large_font)
    w, h = right - left, top - bottom
    draw.text((238-w,-1), text=temp_str, font=large_font, outline=0)
    draw.text((238,7), text='*C')
    draw.text((183,-3), text=current["cond"], font=small_font) #condition

    # wind gauge
    radius = 20 #pixels
    center = (epd_height-radius-1, 64)
    angle, wind_speed = current["wind_dir"], current["wind_spd"]
    draw_windgauge(draw, center, radius, wind_speed, angle)

    # graphical forecast
    #draw_graphical_forecast(epd_width, epd_height, draw, forecast)

    return image


def draw_windgauge(draw, center, radius, wind_spd, angle):
    wind_spd_str = str(wind_spd)
    #w, h = draw.textsize(wind_speed,font=text_font)
    (left, top, right, bottom) = draw.textbbox((0,0), wind_spd_str, font=text_font)
    w, h = right - left, top - bottom
    draw.ellipse((center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius),width=2)
    draw.line([center,(center[0]+radius*math.cos(angle),center[1]-radius*math.sin(angle))], width=3)
    draw.line([center,(center[0]+radius*math.cos(angle-0.8*math.pi),center[1]-radius*math.sin(angle-0.8*math.pi))], width=3)
    draw.line([center,(center[0]+radius*math.cos(angle+0.8*math.pi),center[1]-radius*math.sin(angle+0.8*math.pi))], width=3)
    draw.ellipse((center[0]-radius/2,center[1]-radius/2,center[0]+radius/2,center[1]+radius/2),fill=0)
    draw.text((center[0]-w/2+1,center[1]-h*0.6),text=wind_spd_str,font=text_font,fill=1,align='center')


def draw_graphical_forecast(epd_width, epd_height, draw, forecast):

    min_max = [[99.9,-99.9],[999.9,-1.0],[101.0,-1.0],[101.0,-1.0],[9999.9,-1.0],[101,-1]]

    for i in range(2,len(forecast[0])):
        for j in range(len(forecast)):
            if forecast[j][i] < min_max[i-2][0]:
                min_max[i-2][0] = forecast[j][i]
            if forecast[j][i] > min_max[i-2][1]:
                min_max[i-2][1] = forecast[j][i]

    min_max[1],min_max[2],min_max[3],min_max[5] = [0,min_max[1][1]],[0,100],[0,100],[0,100] #always show certain values in range from 0-100; windspeed, clouds, rain, humidity

    start_label, end_label = forecast[0][0][:10], forecast[len(forecast)-1][0][:10]
    #xborder_right = 108
    forecast_width = 141 #[px]

    #how many lines to draw; subtract two first entries which are just time and date
    data_lines_count = 6 #len(forecast[0])-2

    #width, height = (epd_height-xborder_right)/len(forecast), (epd_width-9)/data_lines_count
    width, height = forecast_width/len(forecast), (epd_width-9)/data_lines_count

    #draw border
    draw.rectangle([(1,epd_width), (forecast_width, epd_width-height*data_lines_count)])

    # draw vertical separators
    for j in range(0, len(forecast)):
        if forecast[j][0][11:13] == "00":
            draw.line([(j*width, epd_width), (j*width,epd_width-height*data_lines_count)], width=1)

    #draw data lines
    for i in range(data_lines_count):

        # horizontal line
        if i != 0:
            draw.line([(0,epd_width-height*i-1), (22,epd_width-height*i-1)])
            draw.line([(forecast_width-37,epd_width-height*i-1), (forecast_width,epd_width-height*i-1)])

        y0 = epd_width-height * (data_lines_count) + (i+1) * height
        value = (float(forecast[0][i+2])-min_max[i][0]) / (min_max[i][1]-min_max[i][0]+0.001) #+0.001 to not divide by zero
        y_left = y0 - height * value

        # draw entries
        polygon_points = [len(forecast)*width, y0, 0, y0] #add lower corners first
        for j in range(0,len(forecast)):
            value = (float(forecast[j][i+2])-min_max[i][0])/(min_max[i][1]-min_max[i][0]+0.001) #+0.001 to not divide by zero
            x = j*width
            y = y0-height*value
            polygon_points += [x,y]

        # draw graph
        draw.polygon(polygon_points, fill=0)

        # draw lables for min and max values of each line
        if i in [0,1,4]: #draw only selected min/max values
            draw.text((forecast_width+20,y0-height*0.5),text=str(min_max[i][0]))
            draw.text((forecast_width+20,y0-height*1.0+1),text=str(min_max[i][1]))

    # labels
    label_font = text_font
    #w,h = draw.textsize('W', font=label_font)
    (left, top, right, bottom) = draw.textbbox((0,0), 'W', font=label_font)
    w, h = right - left, top - bottom
    draw.text((forecast_width+3, epd_width-height*5.5-h/2-1), text='T', font=label_font)
    draw.text((forecast_width+3, epd_width-height*4.5-h/2-1), text='W', font=label_font)
    draw.text((forecast_width+3, epd_width-height*3.5-h/2-1), text='C', font=label_font)
    draw.text((forecast_width+3, epd_width-height*2.5-h/2-1), text='R', font=label_font)
    draw.text((forecast_width+3, epd_width-height*1.5-h/2-1), text='P', font=label_font)
    draw.text((forecast_width+3, epd_width-height*0.5-h/2-1), text='H', font=label_font)

    #w,h = draw.textsize(end_label)
    (left, top, right, bottom) = draw.textbbox((0,0), end_label)
    w, h = right - left, top - bottom
    draw.text((0, epd_width-height*data_lines_count-h), text=start_label)
    draw.text((forecast_width-w, epd_width-height*data_lines_count-h), text=end_label)


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
            print(f"received data: {data}") #debug
        except:
            print("received invalid json data: {line}", flush=True)
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
        epd.display(epd.getbuffer(image))
        epd.sleep() #set epaper display to sleep mode

        print(f"SUCCESS", flush=True)

    epd2in13_V2.epdconfig.module_exit()
    print("TERMINATED", flush=True)

if __name__ == "__main__":
    main()
