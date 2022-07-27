import sys,os,time,requests,math
libdir = '/home/pi/bcm2835-1.60/e-Paper/RaspberryPi_JetsonNano/python/lib' #for epd library
picdir = '/home/pi/bcm2835-1.60/e-Paper/RaspberryPi_JetsonNano/python/pic' #for fonts
if os.path.exists(libdir):
	sys.path.append(libdir)
else:
	print('libdir path not found')
from waveshare_epd import epd2in13_V2
from PIL import Image,ImageDraw,ImageFont

update_interval = 60*60
token = open("openweathermap_token.txt","r").read().rstrip("\n")
#url = "https://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s"%(town,token)
file = open("towns.txt","r")
towns = file.readline().split(",")
#towns = ['Aachen','Hamburg','Detmold','London','Rome,IT','New York']
global town_number
town_number = 0
text_font = ImageFont.truetype(os.path.join(picdir,'Font.ttc'),20)
small_font = ImageFont.truetype(os.path.join(picdir,'Font.ttc'),9)
large_font = ImageFont.truetype(os.path.join(picdir,'Font.ttc'),42)

def update_screen():
	error_file = open("errors.txt","a")
	log_file = open("log.txt","a")
	image = Image.new('1',(epd.height,epd.width),255)
	draw = ImageDraw.Draw(image)
	global town_number
	town = towns[town_number]
	print('1 receiving weather data for '+town)
	log_file.write("\n1 receiving weather data")
	if town_number >= len(towns)-1:
		town_number = 0
	else:
		town_number += 1
	url = "https://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s"%(town,token)
	data = requests.get(url).json()
	print("-data length: "+str(len(data)))

	print('2 drawing weather data')
	log_file.write("\n2 drawing weather data")
	#general info
	w,h = draw.textsize(town)
	draw.text((epd.height-w,epd.width-10-h),text=town)
	_time_ = time.strftime('%H:%M:%S')
	w,h = draw.textsize(_time_)
	draw.text((epd.height-w,epd.width-h),text=_time_)

	#main weather info
	temp = str(int(round(data['main']['temp']-273.15,0)))
	w,h = draw.textsize(temp,font=large_font)
	draw.text((46-w,-9),text=temp,font=large_font,outline=0)
	draw.text((47,-4),text='*C',font=text_font)
	condition = str(data['weather'][0]['description'])
	draw.text((47,12),text=condition,font=text_font)

	#wind gauge
	radius = 20
	center = (epd.height-radius-1,radius)
	angle = (float(data['wind']['deg'])/180.0)*math.pi-math.pi
	wind_speed = str(m_s_to_beaufort(data['wind']['speed']))
	log_file.write("\n3 draw wind gauge")
	draw_windgauge(draw,center,radius,wind_speed,angle)

	#forecast info
	print("4 receiving forecast data")
	log_file.write("\n4 receiving forecast data")
	data_points = 40 #max = 5 days * 8 update times = 40
	forecast_data = []
	url = "https://api.openweathermap.org/data/2.5/forecast?q=%s&%i&appid=%s"%(town,data_points,token)
	url_data = requests.get(url).json()
	print("-forecast data length: "+str(len(url_data)))

	file = open("weather_log.txt","a")
	gather_flag = True if time.localtime().tm_hour == 0 else False #prediction data for next five days will be saved each day at midnight
	for i in range(len(url_data["list"])): #add all interesting forecast data points to the array used to draw the graphs
		t = int(round(url_data['list'][i]['main']['temp']-273.15,0))
		s = round(url_data['list'][i]['wind']['speed'],1)
		c = url_data['list'][i]['clouds']['all'] #cloud cover percentage
		r = int(url_data['list'][i]['pop']*100) #probability of precipitation
		p = url_data['list'][i]['main']['pressure']
		h = url_data['list'][i]['main']['humidity']
		forecast_data.append([t,s,c,r,p,h])

		if gather_flag:
			if url_data['list'][i]['dt_txt'][11:13] in ["00","06","12","18"]: #once a day save the forecast for four points each day for the next five days to file, for analysis how accurate the forecast is depending how far it predicts the weather
				prediction = str(url_data['list'][i]['dt'])+"-"+str(t)+"-"+str(s)+"-"+str(c)+"-"+str(r)+"-"+str(p)+"-"+str(h)
				file.write(prediction+" ")
	if gather_flag:
		file.write("\n")
	if time.localtime().tm_hour in [0,6,12,18]: #four times a day save the actual weather for comparision to the forecast that was made
		t = int(round(data["main"]["temp"],0))
		s = round(data["wind"]["speed"],1)
		c = data["clouds"]["all"]
		p = data["main"]["pressure"]
		h = data["main"]["humidity"]
		try:
			r = data["rain"]["1h"]
		except Exception as e:
			error_file.write("\nError in weather data: "+str(e)+"\n")
			r = 0
		prediction = str(data['dt'])+"-"+str(t)+"-"+str(s)+"-"+str(c)+"-"+str(r)+"-"+str(p)+"-"+str(h)
		file.write(prediction+"\n")
	file.close()
	gather_flag = False

	min_max = [[99.9,-99.9],[999.9,-1.0],[101.0,-1.0],[101.0,-1.0],[9999.9,-1.0],[101,-1]] #min/max for each value
	for i in range(len(forecast_data[0])):
		for j in range(len(forecast_data)):
			if forecast_data[j][i] < min_max[i][0]:
				min_max[i][0] = forecast_data[j][i]
			if forecast_data[j][i] > min_max[i][1]:
				min_max[i][1] = forecast_data[j][i]
	start,end = str(url_data['list'][0]['dt_txt'][0:10]),str(url_data['list'][len(forecast_data)-1]['dt_txt']) #start and end time
	draw_graphical_forecast(draw,forecast_data,min_max,start,end)
	log_file.write("\n5 drawing graphical forecast")

	#update display
	print("6 updating display")
	log_file.write("\n6 updating display")
	epd.display(epd.getbuffer(image))
	log_file.close()
	error_file.close()

def m_s_to_beaufort(speed):
	beaufort_scale = [0.5,1.5,3.3,5.5,7.9,10.7,13.8,17.1,20.7,24.4,28.4,32.6]
	for i in range(len(beaufort_scale)):
		if speed <= beaufort_scale[i]:
			return i
	return 12

def draw_windgauge(draw,center,radius,wind_speed,angle):
	print("3 drawing wind gauge")
	w,h = draw.textsize(wind_speed,font=text_font)
	draw.ellipse((center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius),width=2)
	draw.line([center,(center[0]+radius*math.cos(angle),center[1]-radius*math.sin(angle))],width=5)
	draw.line([center,(center[0]+radius*math.cos(angle+math.pi),center[1]-radius*math.sin(angle+math.pi))])
	draw.ellipse((center[0]-radius/2,center[1]-radius/2,center[0]+radius/2,center[1]+radius/2),fill=0)
	draw.text((center[0]-w/2,center[1]-h*7/11),text=wind_speed,font=text_font,fill=1,align='center')

def draw_graphical_forecast(draw,forecast_data,min_max,start,end):
	print("5 drawing graphical forecast")
	xborder_right = 60
	width,height = (float(epd.height-xborder_right-20))/len(forecast_data),82/len(forecast_data[0])
	draw.rectangle([(1,epd.width),(epd.height-xborder_right,epd.width-height*len(forecast_data[0]))]) #draw border
	for i in range(len(forecast_data[0])): #draw lines
		draw.line([(0,epd.width-height*i-1),(epd.height-xborder_right,epd.width-height*i-1)]) #horizontal line
		y0 = epd.width-height*(len(forecast_data[0]))+(i+1)*height
		value = (float(forecast_data[0][i])-min_max[i][0])/(min_max[i][1]-min_max[i][0]+0.001)
		y_left = y0-height*value
		for j in range(1,len(forecast_data)): #draw entries
			draw.line([(j*width,epd.width),(j*width,epd.width-height*len(forecast_data[0]))]) #vertical line
			value = (float(forecast_data[j][i])-min_max[i][0])/(min_max[i][1]-min_max[i][0]+0.001)
			y_right = y0-height*value
			draw.line([((j-1)*width,y_left),(j*width,y_right)],width=3) #graph line
			y_left = y_right
		draw.text((epd.height-xborder_right-23,y0-height*1.1),text=str(min_max[i][1]))
		draw.text((epd.height-xborder_right-23,y0-height*0.58),text=str(min_max[i][0]))

	w,h = draw.textsize('W')
	draw.text((epd.height-xborder_right+3,epd.width-height*5.5-h/2),text='T') #labels
	draw.text((epd.height-xborder_right+3,epd.width-height*4.5-h/2),text='W')
	draw.text((epd.height-xborder_right+3,epd.width-height*3.5-h/2),text='C')
	draw.text((epd.height-xborder_right+3,epd.width-height*2.5-h/2),text='R')
	draw.text((epd.height-xborder_right+3,epd.width-height*1.5-h/2),text='P')
	draw.text((epd.height-xborder_right+3,epd.width-height*0.5-h/2),text='H')
	w = draw.textsize(end)[0]
	draw.text((0,epd.width-height*len(forecast_data[0])-h),text=start)
	draw.text((epd.height-xborder_right-w,epd.width-height*len(forecast_data[0])-h),text=end)

try:
	print('0 start and initialise e-paper module')
	epd = epd2in13_V2.EPD()
	epd.init(epd.FULL_UPDATE)
	epd.Clear(0xFF)

	while True:
		with open("log.txt","a") as log_file:
			log_file.write("\n\n"+str(time.asctime(time.localtime()))+" updating")
		epd.init(epd.FULL_UPDATE)
#		try:
#			update_screen() #getting weather data and drawing the screen graphics
#		except Exception as e:
#			with open("errors.txt","a") as file:
#				file.write(time.asctime(time.localtime())+" error in update_screen: "+str(e)+"\n")
		update_screen()
		print('power saving mode (Ctrl+c to stop program)')
		epd.sleep()
		time.sleep(update_interval)

except IOError as e:
	print(e)

except KeyboardInterrupt:
	print('\nProgram stopped')
	epd2in13_V2.epdconfig.module_exit()
	exit()
