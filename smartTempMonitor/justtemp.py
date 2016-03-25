#!/usr/bin/python
 
import subprocess
import re
import sys
import time
import datetime
import gspread


email 		= 'alexman.hdz@gmail.com'   #this is your full gmail address
password 	= 'zwtvwlypujxfmttg'        #this is your gmail password
spreadsheet_name= "SmartRasPi Docs"
worksheet_name 	= "Temp_Humidity"

dht_driver      = "22"
dht_gpio        = "4"
myTimer         = 1 # 2 minutes

myZone          = "Zone-I"
loop            = True


 
# Append data
while(loop):
  output = subprocess.check_output(["/home/pi/smartdev/Adafruit_DHT", dht_driver, dht_gpio]);
#  print output   # DEBUG

  matches = re.search("Temp =\s+([0-9.]+)", output)
  if (not matches):
    values = [datetime.datetime.now(), myZone, "", "", "", "Error Reading Temp"]
    continue

  tempC = float(matches.group(1))
 
  tempF = tempC * 9.0;
  tempF = tempF / 5.0;
  tempF = tempF + 32.0;
 
  matches = re.search("Hum =\s+([0-9.]+)", output)
  if (not matches):
    values = [datetime.datetime.now(), myZone, "", "", "", "Error Reading Humidity"]
    continue
 
  humidity = float(matches.group(1))

#  print values[0]
#  print values[1]
  print datetime.datetime.now()

  
#  print "Temperature: %.1f C" % tempC
#  print "Temperature: %.1f F" % tempF
#  print "Humidity:    %.1f %%" % humidity

  print "%.1f C" % tempC + ';' + "%.1f F" % tempF  + ';' + "%.1f %%" % humidity
#

  print '' 
  loop=False

#print "Done..."
sys.exit()
