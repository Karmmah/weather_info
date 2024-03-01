#script providing functions for creating an image from weather and forecast data

import time, os, math, subprocess
from PIL import Image,ImageDraw,ImageFont

picdir = '/home/pi/weather_info' #where fonts are located

text_font = ImageFont.truetype(os.path.join(picdir,'Font.ttc'),20)
small_font = ImageFont.truetype(os.path.join(picdir,'Font.ttc'),9)
large_font = ImageFont.truetype(os.path.join(picdir,'Font.ttc'),42)

#data structures:
#current data: [temp,condition,wind_angle,wind_speed]
#forecast data for each data point: [z_string,z_float,temp,windspeed,clouds,rain,pressure,humidity


def get_image(epd_width, epd_height, town, current, forecast):
	image = Image.new('1',(epd_height,epd_width),255)
	draw = ImageDraw.Draw(image)

	# draw general info 
	w,h = draw.textsize(town)
	draw.text((epd_height-w, 56), text=town)
	_time_ = time.strftime('%H:%M:%S')
	w,h = draw.textsize(_time_, font=text_font)
	draw.text((175, -5), text=_time_, font=text_font)
	try:
		ip = subprocess.check_output("hostname -I", shell=True, text=True)
		ip = ip.split(" ")[0]
	except:
		ip = "No connection"
	draw.text((epd_height-78, epd_width-10), text = ip)

	# draw big current general weather info
	temp = current[0]
	w,h = draw.textsize(temp,font=large_font)
	draw.text( (238-w,7), text=temp, font=large_font, outline=0 )
	draw.text( (238,17), text='*C')
	condition = current[1]
	draw.text( (183,47), text=condition, font=small_font )

	# draw wind gauge
	radius = 20 #pixels
	center = (epd_height-radius-1, epd_width-radius-13)
	angle,wind_speed = current[2],current[3]
	draw_windgauge(draw,center,radius,wind_speed,angle)

	# draw graphical forecast
	draw_graphical_forecast(epd_width,epd_height,draw,forecast)

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


def draw_windgauge(draw,center,radius,wind_speed,angle):
	w, h = draw.textsize(wind_speed,font=text_font)
	draw.ellipse((center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius),width=2)
	draw.line([center,(center[0]+radius*math.cos(angle),center[1]-radius*math.sin(angle))],width=5)
	draw.line([center,(center[0]+radius*math.cos(angle+math.pi),center[1]-radius*math.sin(angle+math.pi))])
	draw.ellipse((center[0]-radius/2,center[1]-radius/2,center[0]+radius/2,center[1]+radius/2),fill=0)
	draw.text((center[0]-w/2,center[1]-h*7/11),text=wind_speed,font=text_font,fill=1,align='center')


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
	xborder_right = 108

	#how many lines to draw; subtract two first entries which are just time and date
	amount = len(forecast[0])-2
	width, height = (epd_height-xborder_right)/len(forecast), (epd_width-9)/amount
	width *= 0.88 #correction factor for proper layout

	#draw border
	draw.rectangle([(1,epd_width),(epd_height-xborder_right,epd_width-height*amount)])

	#draw lines
	for i in range(amount):
		# horizontal line
		if i!=0:
			draw.line([(0,epd_width-height*i-1), (22,epd_width-height*i-1)])
			draw.line([(epd_height-xborder_right-37,epd_width-height*i-1), (epd_height-xborder_right,epd_width-height*i-1)])

		y0 = epd_width-height*(amount)+(i+1)*height
		value = (float(forecast[0][i+2])-min_max[i][0])/(min_max[i][1]-min_max[i][0]+0.001)
		y_left = y0-height*value

		# draw entries
		polygon_points = [epd_height-xborder_right,y0,0,y0]
		for j in range(0,len(forecast)):
			# draw vertical separators on first line
			if i == 0:
				# vertical lines; at the start of each day
				if forecast[j][0][11:13] == "00":
#					draw.line([(j*width,epd_width),(j*width,epd_width-height*amount)], width=2)
					draw.line([(j*width,epd_width),(j*width,epd_width-height*amount)])

				# at the other data points
				else:
					pass #draw.line([(j*width,epd_width),(j*width,epd_width-height*amount)], width=1)

			value = (float(forecast[j][i+2])-min_max[i][0])/(min_max[i][1]-min_max[i][0]+0.001)
			x = j*width
			y = y0-height*value
			polygon_points += [x,y]

		# draw graph
		draw.polygon(polygon_points, fill=0)

		# draw lables for min and max values of each line
		if i in [0,1,4]:
			draw.text((epd_height-xborder_right+20,y0-height*0.5),text=str(min_max[i][0]), font=small_font)
			draw.text((epd_height-xborder_right+20,y0-height*1.0),text=str(min_max[i][1]), font=small_font)

	# labels
	label_font = text_font
	w,h = draw.textsize('W', font=label_font)

	draw.text( (epd_height-xborder_right+2, epd_width-height*5.5-h/2-1), text='T', font=label_font)
	draw.text( (epd_height-xborder_right+2, epd_width-height*4.5-h/2-1), text='W', font=label_font)
	draw.text( (epd_height-xborder_right+2, epd_width-height*3.5-h/2-1), text='C', font=label_font)
	draw.text( (epd_height-xborder_right+2, epd_width-height*2.5-h/2-1), text='R', font=label_font)
	draw.text( (epd_height-xborder_right+2, epd_width-height*1.5-h/2-1), text='P', font=label_font)
	draw.text( (epd_height-xborder_right+2, epd_width-height*0.5-h/2-1), text='H', font=label_font)

	w,h = draw.textsize(end_label)
	draw.text((0, epd_width-height*amount-h), text=start_label)
	draw.text((epd_height-xborder_right-w, epd_width-height*amount-h), text=end_label)
