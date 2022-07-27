#analyse accuracy of five day weather prediction from openweathermap based on data gathered by weather.py

def analyse(data):
	pass

def main():
	path = input("Input File Name with full path: ")
	try:
		f = open(path)
		lines = f.read().split("\n")
		for item in lines:
			if item[0:1] == "C":
				print("C")
			elif item[0:1] == "F":
				print("F")
			else:
				print("Unrecognised entry: %s"%(item))

	except Exception as e:
		print(e)

if __name__ == "__main__":
	main()
