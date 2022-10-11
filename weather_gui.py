#script providing functions for creating an image from weather and forecast data

import time,os,math
from PIL import Image,ImageDraw,ImageFont

picdir = '/home/pi/weather_info' #where fonts are located

text_font = ImageFont.truetype(os.path.join(picdir,'Font.ttc'),20)
small_font = ImageFont.truetype(os.path.join(picdir,'Font.ttc'),9)
large_font = ImageFont.truetype(os.path.join(picdir,'Font.ttc'),42)

#data structures:
#current data: [temp,condition,wind_angle,wind_speed]
#forecast data for each data point: [z_string,z_float,temp,windspeed,clouds,rain,pressure,humidity

def get_image(epd_width, epd_height, town, current, forecast): #return an image created from data
	image = Image.new('1',(epd_height,epd_width),255)
	draw = ImageDraw.Draw(image)

	#general info (town and time)
	w,h = draw.textsize(town)
	draw.text((epd_height*0.3, -h*0.3), text=town)
	_time_ = time.strftime('%H:%M:%S')
	w,h = draw.textsize(_time_)
	draw.text((epd_height*0.3, h*0.55), text=_time_)

	#main weather info
	temp = current[0]
	w,h = draw.textsize(temp,font=large_font)
	draw.text((46-w,-9),text=temp,font=large_font,outline=0)
	draw.text((47,-4),text='*C',font=text_font)
	condition = current[1]
	draw.text((47,12),text=condition,font=text_font)

	#wind gauge
	radius = 25 #pixels
	center = (epd_height-radius-1,radius)
	angle,wind_speed = current[2],current[3]
	draw_windgauge(draw,center,radius,wind_speed,angle)

	min_max = [[99.9,-99.9],[999.9,-1.0],[101.0,-1.0],[101.0,-1.0],[9999.9,-1.0],[101,-1]] #min/max for temp,windspeed,clouds,rain,pressure,humidity
	for i in range(2,len(forecast[0])):
		for j in range(len(forecast)):
			if forecast[j][i] < min_max[i-2][0]:
				min_max[i-2][0] = forecast[j][i]
			if forecast[j][i] > min_max[i-2][1]:
				min_max[i-2][1] = forecast[j][i]
	min_max[1],min_max[2],min_max[3],min_max[5] = [0,min_max[1][1]],[0,100],[0,100],[0,100] #always show certain values in range from 0-100; windspeed, clouds, rain, humidity
	start,end = forecast[0][0][0:10],forecast[len(forecast)-1][0]
	draw_graphical_forecast(epd_width,epd_height,draw,forecast,min_max,start,end)

	try:
		draw_today(draw, forecast, min_max, epd_width, epd_height)
	except Exception as e:
		print(e)
	return image

##forecast data for each data point: [0:z_string,1:z_float,2:temp,3:windspeed,4:clouds,5:rain,6.pressure,7:humidity]
##min/max for temp,windspeed,clouds,rain,pressure,humidity
def draw_today(draw, forecast, min_max, epd_width, epd_height):
	#draw a few select infos for the current day in extra graphic
	amount = 4 #how many infos to draw; infos to draw: temp, windspeed, cloud, rain
	width, height = 49, 68
	line_height = (height-10)/amount
	draw.rectangle([(epd_height-width,epd_width-1),(epd_height-1,epd_width-height)]) #draw border

	draw.text((epd_height-width+3, epd_width-height), text="Today")
	for i in range(amount):
		draw.line([ epd_height-width, epd_width-line_height*(amount-i), epd_height, epd_width-line_height*(amount-i) ]) #divider line

		draw.text( (epd_height-30,epd_width-line_height*(amount+i)) ,text="field"+str(i), font=text_font, fill=0, align='center')
		for j in range(1, len(forecast[2])):
			y0 = epd_width-line_height*i - line_height * (forecast[j-1][i+2]-min_max[i][0]) / (min_max[i][1]-min_max[i][0])
			y1 = epd_width-line_height*i - line_height * (forecast[j][i+2]-min_max[i][0])/(min_max[i][1]-min_max[i][0])
			x0 = epd_height-width+j*width/len(forecast[2])
			x1 = x0 + width/len(forecast[2])
			draw.line([x0,y0,x1,y1])
			y0 = y1

def draw_windgauge(draw,center,radius,wind_speed,angle):
	w, h = draw.textsize(wind_speed,font=text_font)
	draw.ellipse((center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius),width=2)
	draw.line([center,(center[0]+radius*math.cos(angle),center[1]-radius*math.sin(angle))],width=5)
	draw.line([center,(center[0]+radius*math.cos(angle+math.pi),center[1]-radius*math.sin(angle+math.pi))])
	draw.ellipse((center[0]-radius/2,center[1]-radius/2,center[0]+radius/2,center[1]+radius/2),fill=0)
	draw.text((center[0]-w/2,center[1]-h*7/11),text=wind_speed,font=text_font,fill=1,align='center')

def draw_graphical_forecast(epd_width, epd_height, draw, forecast, min_max, start, end):
	xborder_right = 60
	amount = len(forecast[0])-2 #how many lines to draw; subtract two first entries which are just time and date
	width, height = (epd_height-xborder_right)/len(forecast),82/amount
	width *= 0.88 #correction factor for proper layout
#	width *= 1.05 #correction factor for proper layout (used with python2)
#	draw.rectangle([(1,epd_width),(epd_height-xborder_right,epd_width-height*amount)]) #draw border

	for i in range(amount): #draw lines
		if i!=0:
			draw.line([(0,epd_width-height*i-1), (epd_height-xborder_right,epd_width-height*i-1)]) #horizontal line
		y0 = epd_width-height*(amount)+(i+1)*height
		value = (float(forecast[0][i+2])-min_max[i][0])/(min_max[i][1]-min_max[i][0]+0.001)
		y_left = y0-height*value

		for j in range(0,len(forecast)): #draw entries
			if i == 0: #draw vertical separators on first line
				if forecast[j][0][11:13] == "00": #vertical lines; print a wider line at the start of each day
					draw.line([(j*width,epd_width),(j*width,epd_width-height*amount)], width=2)
				else:
					draw.line([(j*width,epd_width),(j*width,epd_width-height*amount)], width=1)
			value = (float(forecast[j][i+2])-min_max[i][0])/(min_max[i][1]-min_max[i][0]+0.001)
			y_right = y0-height*value
			draw.line([((j-1)*width,y_left), (j*width,y_right)], width=3) #graph line
			y_left = y_right

		draw.text((epd_height-xborder_right-23,y0-height*1.1),text=str(min_max[i][1])) #min and max values of each line
		draw.text((epd_height-xborder_right-23,y0-height*0.58),text=str(min_max[i][0]))

	w,h = draw.textsize('W')
	draw.text((epd_height-xborder_right+2,epd_width-height*5.5-h/2),text='T') #labels
	draw.text((epd_height-xborder_right+2,epd_width-height*4.5-h/2),text='W')
	draw.text((epd_height-xborder_right+2,epd_width-height*3.5-h/2),text='C')
	draw.text((epd_height-xborder_right+2,epd_width-height*2.5-h/2),text='R')
	draw.text((epd_height-xborder_right+2,epd_width-height*1.5-h/2),text='P')
	draw.text((epd_height-xborder_right+2,epd_width-height*0.5-h/2),text='H')

	w = draw.textsize(end)[0]
	draw.text((0, epd_width-height*amount-h), text=start)
	draw.text((epd_height-xborder_right-w, epd_width-height*amount-h), text=end)
