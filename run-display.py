# Python script to display current Covid-19 cases on a 16x2 display
# Author: Maximilian Krause
# Date: 15.06.2020

# ############
# Define Var
version = "1.0"
country = "Germany"
errormsg = "Null"
update_intervall = 600 # 10 Minutes
# ############

# Define Error Logging
def printerror(ex):
	print('\033[31m' + str(ex) + '\033[0m')

def printwarning(warn):
	print('\033[33m' + str(warn) + '\033[0m')


# Do all imports
print("Loading modules")
try:
	import time
	from signal import signal, SIGINT
	import sys
	from datetime import datetime, date, timedelta
	import json
	import requests
	from os import system, name
	import argparse
	import lcddriver
except ModuleNotFoundError:
	printerror("The app could not be started.")
	printerror("Please run 'sudo ./install.sh' first.")
	exit(2)
except:
	printerror("An unknown error occured while loading modules.")
	exit(2)

# Check for arguments
# Check for other arguments later in main
parser = argparse.ArgumentParser()
parser.add_argument("--version", "-v", help="Prints the version", action="store_true")
parser.add_argument("--backlightoff", "-b", help="Turns off the backlight of the lcd", action="store_true")
parser.add_argument("--list", "-l", help="Shows a list of available countries", action="store_true")
parser.add_argument("--timer", "-t", type=int, help="Shows a list of available countries")
parser.add_argument("--country", "-c",  type=str, help="Select a different county once.", action='store')

args = parser.parse_args()
if args.version:
	print(str(version))
	exit(0)

if args.timer:
	printwarning("Set new timer to " + str(args.timer))
	update_intervall = args.timer

if args.country:
	printwarning("Selected different country: " + args.country)
	country = args.country

# Load driver for LCD display
try:
	display = lcddriver.lcd()

	#Check backlight option
	if args.backlightoff:
		printwarning("Option: Backlight turned off!")
		display.backlight(0)
	else:
		display.backlight(1)

	display.lcd_display_string("Loading display", 1)
	display.lcd_display_string("V " + str(version), 2)
	time.sleep(1.5)
except IOError:
	printerror("The connection to the display failed.")
	printerror("Please check your connection for all pins.")
	printerror("From bash you can run i2cdetect -y 1")

	printerror("Would you like to proceed anyway (More errors might occur)? [y/n]")
	yes = {'yes', 'y'}
	no = {'no', 'n'}
	choice = input().lower()
	if choice in yes:
		print("Will continue...")
	elif choice in no:
		print("Shutting down... Bye!")
		exit(1)
	else:
		print("Please choose yes or no")
except Exception as e:
	printerror("An unknown error occured while connecting to the lcd.")
	printerror(e)


#Check or internet connection
def is_connected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

#Handles Ctrl+C
def handler(signal_received, frame):
	# Handle any cleanup here
	print()
	printwarning('SIGINT or CTRL-C detected. Please wait until the service has stopped.')
	if errormsg == "Null":
		display.lcd_clear()
		display.lcd_display_string("Manual cancel.", 1)
		display.lcd_display_string("Exiting app.", 2)
	else:
		display.lcd_clear()
		display.lcd_display_string(str(errormsg), 1)
		display.lcd_display_string("Exiting app.", 2)
	exit(0)

# Print all available countries
def readCountries(p=False):
	try:
		print("Reading list of all countries")
		r = requests.get('https://www.trackcorona.live/api/countries')
		if r.status_code == 200:
			print("Retrieved all country data")
			json_data_countries = json.loads(r.text)
			for item in json_data_countries['data']:
				if p == True:
					print("ID: " + item['country_code'] + "		| last update: " + item['updated'] + "		| Country: " + item['location'])
			return json_data_countries
		else:
			print("Failed contacting server")
			print(r.raise_for_status())
			exit(3)
	except Exception as e:
		print("Failed reading countries, something unexpected happened.")
		print(e)
		exit()

# Clears the display
def clear():
	# for windows
	if name == 'nt':
		_ = system('cls')

	# for mac and linux(here, os.name is 'posix')
	else:
		_ = system('clear')

#Countdown in seconds
def countdown(t):
	total = t
	progvalue = 0

	while t:
		mins, secs = divmod(t, 60)
		timer = '{:02d}:{:02d}'.format(mins, secs)
		print("Time until next run: " + timer, end="\r")
		time.sleep(1)
		t -= 1
	print(" ", end="\r")

# Get selected country information
def getCountryInfo():
	print("Reading country information for " + country)
	if not country:
		printerror("Country must not be empty!")
		exit(0)

	# Get correct country from ISO2 Code
	country_list = readCountries()
	id = ""
	for i in country_list['data']:
		print("Checking " + i['location'], end="\r")
		if i['location'] == country:
			# id = i['moreData'].split("/")[5]
			id = i['country_code']
			print("Selected country " + i['location'] + " with ID " + i['country_code'])
		sys.stdout.write("\033[K") # Clear to the end of line

	if not id:
		printerror("Country " + country + " could not be found!")
		exit(4)

	try:
		url = "https://www.trackcorona.live/api/countries/" + id
		print("Getting data from " + url)
		r = requests.get(url)
		if r.status_code == 200:
			country_json = json.loads(r.text)
			return country_json
		else:
			printerror("Could not connect to server")
			print(r.raise_for_status())
			exit(3)
	except Exception as e:
		printerror("Failed reading country information, something unexpected happended.")
		printerror(e)
		exit()

# Return value from json
def readInfected(json):
	try:
		return json['data'][0]['confirmed']
	except Exception as e:
		printwarning("Failed reading infected status!")
		return "N/A"

# Return value from json
def readDeceased(json):
        try:
                return json['data'][0]['dead']
        except Exception as e:
                printwarning("Failed reading deceased status!")
                return "N/A"

# Return value from json
def readRecovered(json):
        try:
                return json['data'][0]['recovered']
        except Exception as e:
                printwarning("Failed reading recovered status!")
                return "N/A"
# Return value from json
def readUpdated(json):
        try:
                return json['data'][0]['updated']
        except Exception as e:
                printwarning("Failed reading last update status!")
                return "N/A"

# Display active cases
def displayActive():
	while(True):
		# Read country info
		display.lcd_display_string("Retreiving data", 2)
		c = getCountryInfo()

		# Assign data
		infected = readInfected(c)
		updated = readUpdated(c).split('.')[0]
		deceased = readDeceased(c)
		recovered = readRecovered(c)
		try:
			active = infected - deceased - recovered
		except:
			printerror("Unable to calculate active cases.")
			active = "N/A"

		# Display data external
		display.lcd_clear()
		display.lcd_display_string(country, 1)
		display.lcd_display_string("Active: " + str(active), 2)

		clear()
		print("===== " + country + " =====")
		print("Infected:		" + str(infected))
		print("Deceased:		" + str(deceased))
		print("Recovered:		" + str(recovered))
		print("Active:			" + str(active))
		print("Last API Update:	" + str(updated))
		print()

		countdown(update_intervall)

# Main
if __name__ == '__main__':
	# Tell Python to run the handler() function when SIGINT is recieved
	signal(SIGINT, handler)

	# Check for remaining arguments here
	if args.list:
		readCountries(p=True)
		display.lcd_clear()
		display.lcd_display_string("Printed list", 1)
		display.lcd_display_string("of all countries", 2)
		exit(0)

	displayActive()
