#!/usr/bin/python
 
import subprocess
import re
import os
import sys
import time
import datetime
import gspread
import string

email 		= 'alexman.hdz@gmail.com'   #this is your full gmail address
password 	= 'zwtvwlypujxfmttg'        #this is your gmail password
spreadsheet_name= "SmartRasPi Docs"

worksheet_name 	= "Temp_Humidity"

dht_driver      = "22"
dht_gpio        = "4"
myTimer         = 1 # 2 minutes

myZone          = "Zone-B"
loop            = True


#update worksheet tab
worksheet_name=worksheet_name + "_" + myZone


#Login
try:
	gc = gspread.login(email,password)
except:
	print "Unable to login. Check email/pswd"
	sys.exit()

#Open spreadsheet
try:
	sh = gc.open(spreadsheet_name)

except:
	print "Unable to open spreadsheet"
	print "Check your spreadsheet name: %s" % spreadsheet_name
	sys.exit()

try:
	worksheet = sh.worksheet(worksheet_name)
except:
	print "Unable to select a sheet"
	print "Check your worksheet name: %s" % worksheet_name
	sys.exit()

 
# Append data
while(loop):
  output = subprocess.check_output(["/home/pi/smartdev/Adafruit_DHT", dht_driver, dht_gpio]);
  print output   # DEBUG

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
 
  print "Temperature: %.1f C" % tempC
  print "Temperature: %.1f F" % tempF
  print "Humidity:    %.1f %%" % humidity
 
  values = [datetime.datetime.now(), myZone, tempC, tempF, humidity]
#  print "values:" 
#  print values
#  print time.time()

  cmd="echo " +string(datetime.datetime.now()) +":"   +string(myZone) +":"  +string(tempC) +":" +string(tempF) +":" +string(humidity)

#+" > " +time.time()
  


  print cmd 

 # os.system("echo %s" % values)

#  try:
#    worksheet.append_row(values)
#  except:
#    print "Unable to append data.  Check your connection?"
#    sys.exit()
 
  loop=False

print "Done..."
sys.exit()
