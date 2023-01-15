import time

def calc_deltas(current_data, forecast_data):
	print("len(current_data):\n", len(current_data), "current_data[0]:", current_data[0])
	print("len(forecast_data):\n", len(forecast_data), "forecast_data[0]:", forecast_data[0])

	for current in current_data:
		temp_delta = {"1d_sum":0, "1d_amount":0, "2d_sum":0, "2d_amount":0, "3d_sum":0, "3d_amount":0, "4d_sum":0, "4d_amount":0, "5d_sum":0, "5d_amount":0}

		for forecast_block in forecast_data:
			#skip the block if current time is not in the prediction time range
			if current["time"] < forecast_block[0]["time"] or current["time"] > forecast_block[len(forecast_block)-1]["time"]:
				continue

			for entry in forecast_block:
				delta_time = int(entry["time"])-current["time"]

				#look for prediction in the forecast corresponding to the point in current_data
				if abs(delta_time) < 3600*1.5:
					forecast_time_offset = round((entry["time"]-forecast_block[0]["time"])/3600/24, 0)

					if forecast_time_offset == 1:
						temp_delta["1d_sum"] += entry["temp"]-current["temp"]
						temp_delta["1d_amount"] += 1
					if forecast_time_offset == 2:
						temp_delta["2d_sum"] += entry["temp"]-current["temp"]
						temp_delta["2d_amount"] += 1
					if forecast_time_offset == 3:
						temp_delta["3d_sum"] += entry["temp"]-current["temp"]
						temp_delta["3d_amount"] += 1
					if forecast_time_offset == 4:
						temp_delta["4d_sum"] += entry["temp"]-current["temp"]
						temp_delta["4d_amount"] += 1
					if forecast_time_offset == 5:
						temp_delta["5d_sum"] += entry["temp"]-current["temp"]
						temp_delta["5d_amount"] += 1

		print("temp delta avg:")
		if temp_delta["1d_amount"] > 0:
			print("  1d", temp_delta["1d_sum"]/temp_delta["1d_amount"])
		if temp_delta["2d_amount"] > 0:
			print("  2d", temp_delta["2d_sum"]/temp_delta["2d_amount"])
		if temp_delta["3d_amount"] > 0:
			print("  3d", temp_delta["3d_sum"]/temp_delta["3d_amount"])
		if temp_delta["4d_amount"] > 0:
			print("  4d", temp_delta["4d_sum"]/temp_delta["4d_amount"])
		if temp_delta["5d_amount"] > 0:
			print("  5d", temp_delta["5d_sum"]/temp_delta["5d_amount"])

def main():
	# define or ask for the file name
	print("Input file name: ", end="")
#	file_name = input()
	file_name = "weather_log_230112.txt" #testing, debug

	print(file_name) #testing, debug

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
				current_data.append( {"time":int(line[2]), "temp":int(line[3])} ) #, "wind_speed":float(line[6])} ) , "wind_angle":line[5]})

			elif line[0] == "Forecast:":
				forecast = []

				for entry in line:
					#skip the signifier at the beginning of the line
					if entry == "Forecast:":
						continue

					data = entry.split("-")

					forecast.append( {"time":int(data[0]), "temp":int(data[1])} ) #, "wind_speed":float(entry[2])} )

				forecast_data.append(forecast)

			else:
				break

		calc_deltas(current_data, forecast_data)

if __name__ == "__main__":
	print("Starting the weather log analysis")
	main()
