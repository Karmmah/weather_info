#script providing functions for creating an image from weather and forecast data

import time, os, math, subprocess, sys
from PIL import Image,ImageDraw,ImageFont

repo_path = os.path.dirname(os.path.abspath(__file__)).rstrip("src/")
sys.path.append(repo_path)

picdir = '/home/pi/weather_info/lib' #where fonts are located
text_font = ImageFont.truetype(os.path.join(picdir,'Font.ttc'),20)
small_font = ImageFont.truetype(os.path.join(picdir,'Font.ttc'),9)
large_font = ImageFont.truetype(os.path.join(picdir,'Font.ttc'),42)

#data structures:
#current data: [temp,condition,wind_angle,wind_speed]
#forecast data for each data point: [z_string,z_float,temp,windspeed,clouds,rain,pressure,humidity


def get_image(epd_width, epd_height, town, current, forecast):

	image = Image.new('1',(epd_height,epd_width),255)
	draw = ImageDraw.Draw(image)

	# add town and time info 
	#time_str = time.strftime('%H:%M:%S')
	time_str = time.strftime('%H:%M')
	w,h = draw.textsize(time_str, font=text_font)
	draw.text((epd_height-w, epd_width-30), text=time_str, font=text_font)
	w,h = draw.textsize(town)
	draw.text((epd_height-w, epd_width-37), text=town)

	# add connection info
	try:
		ip = subprocess.check_output("hostname -I", shell=True, text=True)
		ip = ip.split(" ")[0]
	except:
		ip = "No connection"
	draw.text((epd_height-78, epd_width-10), text = ip)

	# big condition info
	temp = current[0]
	w,h = draw.textsize(temp,font=large_font)
	draw.text((238-w,-1), text=temp, font=large_font, outline=0)
	draw.text((238,7), text='*C')
	draw.text((183,-3), text=current[1], font=small_font) #condition

	# wind gauge
	radius = 20 #pixels
	center = (epd_height-radius-1, 64)
	angle,wind_speed = current[2],current[3]
	draw_windgauge(draw,center,radius,wind_speed,angle)

	# graphical forecast
	draw_graphical_forecast(epd_width, epd_height, draw, forecast)

	return image


def draw_today(draw, forecast, min_max, epd_width, epd_height):
	#graph of the next 24h weather data

	##forecast data for each data point: [0:z_string,1:z_float,2:temp,3:windspeed,4:clouds,5:rain,6.pressure,7:humidity]
	##min/max for temp,windspeed,clouds,rain,pressure,humidity

	#draw a few select infos for the current day in extra graphic
	amount = 4 #how many infos to draw; infos to draw: temp, windspeed, cloud, rain
	width, height = 49, 68
	line_height = (height-10)/amount
	draw.rectangle([(epd_height-width,epd_width-1),(epd_height-1,epd_width-height)]) #draw border

	draw.text((epd_height-width+3, epd_width-height), text=" Today")
	labels = ["T", "W", "C", "R"]

	for i in range(amount):
		# divider line
		draw.line([ epd_height-width, epd_width-line_height*(amount-i), epd_height, epd_width-line_height*(amount-i) ])

		draw.text( (epd_height-46,epd_width-line_height*(amount-i)) ,text=labels[i], font=small_font, fill=0, align='center')
		for j in range(1, len(forecast[2])):
			y0 = epd_width-line_height*(amount-i-1) - line_height * (forecast[j-1][i+2]-min_max[i][0]) / (min_max[i][1]-min_max[i][0])
			y1 = epd_width-line_height*(amount-i-1) - line_height * (forecast[j][i+2]-min_max[i][0])/(min_max[i][1]-min_max[i][0])
			x0 = epd_height-width+j*width/len(forecast[2])
			x1 = x0 + width/len(forecast[2])
			draw.line([x0,y0,x1,y1])
			y0 = y1


def draw_windgauge(draw, center, radius, wind_speed, angle):
	w, h = draw.textsize(wind_speed,font=text_font)
	draw.ellipse((center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius),width=2)
	draw.line([center,(center[0]+radius*math.cos(angle),center[1]-radius*math.sin(angle))], width=3)
	draw.line([center,(center[0]+radius*math.cos(angle-0.8*math.pi),center[1]-radius*math.sin(angle-0.8*math.pi))], width=3)
	draw.line([center,(center[0]+radius*math.cos(angle+0.8*math.pi),center[1]-radius*math.sin(angle+0.8*math.pi))], width=3)
	draw.ellipse((center[0]-radius/2,center[1]-radius/2,center[0]+radius/2,center[1]+radius/2),fill=0)
	draw.text((center[0]-w/2+1,center[1]-h*0.6),text=wind_speed,font=text_font,fill=1,align='center')


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
	forecast_width = 141

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
	w,h = draw.textsize('W', font=label_font)
	draw.text((forecast_width+3, epd_width-height*5.5-h/2-1), text='T', font=label_font)
	draw.text((forecast_width+3, epd_width-height*4.5-h/2-1), text='W', font=label_font)
	draw.text((forecast_width+3, epd_width-height*3.5-h/2-1), text='C', font=label_font)
	draw.text((forecast_width+3, epd_width-height*2.5-h/2-1), text='R', font=label_font)
	draw.text((forecast_width+3, epd_width-height*1.5-h/2-1), text='P', font=label_font)
	draw.text((forecast_width+3, epd_width-height*0.5-h/2-1), text='H', font=label_font)

	w,h = draw.textsize(end_label)
	draw.text((0, epd_width-height*data_lines_count-h), text=start_label)
	draw.text((forecast_width-w, epd_width-height*data_lines_count-h), text=end_label)
