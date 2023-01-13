import time

def calc_deltas(current_data, forecast_data):
	print("currnet_data[0]:", current_data[0])
	print("forecast_data[0]:", forecast_data[0])

	for c in current_data:
		current_time = c["time"]
		print(current_time)

		for f in forecast_data:

			for e in f:
				delta_time = int(e[0])-current_time
				if abs(delta_time) < 3600*2:
					print(delta_time)

def main():
	# define or ask for the file name
	print("Input file name: ", end="")
#	file_name = input()
	file_name = "weather_log_230112.txt" #testing, debug

	print(file_name) #debug

	# check if the file exists
	try:
		open(file_name)

	except:
		print("No file with that name")
#		main()

	# read and analyze the data from the file
	with open(file_name) as f:

		current_data = []
		forecast_data = []

		while True:
			line = f.readline().rstrip(" \n").split(" ")

#data structures:
#current: [info,z_string,z_int,temp,condition,wind_angle,wind_speed]
#forecast (for each entry): [z_string,z_float,t,s,c,r,p,h]
##			for item in current:
##				print(item)
##				log.write(str(item) + " ")
##			for item in forecast:
##				log.write(item[1]+"-"+str(item[2])+"-"+str(item[3])+"-"+str(item[4])+"-"+str(item[5])+"-"+str(item[6])+"-"+str(item[7]))

			if line[0] == "Current:":
#				print(time.strftime("%d.%m.%y %H:%M:%S", time.gmtime(int(line[2])))) #debug
				current_data.append({"time":int(line[2]), "temp":int(line[3]), "wind_speed":float(line[6])}) #, "wind_angle":line[5]})

			elif line[0] == "Forecast:":
				forecast = []

				for s in line:
					if s == "Forecast:":
						continue
					forecast.append(s.split("-"))

				forecast_data.append(forecast)

			else:
				break

		calc_deltas(current_data, forecast_data)

if __name__ == "__main__":
	print("Starting the weather log analysis")
	main()
