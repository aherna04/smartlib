#!/usr/bin/python

#This is a script to post information about a headless system to a google spreadsheet for access and logging
#You will need to create a google spreadsheet in google drive the name is not important as it is referenced by the 
#unique key below but the first row (headers) must match the headers in the dictionary lower down.
#my headers are    ///   time   date   locip   pubip   uptime      ///      google inserts into the first match of each
#This script depends on the google python data API (sudo apt-get install python-gdata)

#I have this set up in cron to run hourly which also means it runs just after boot also.
#A cool feature of google docs is that you can subscirbe to document changes which means you will get an email everytime its updated
#(if you subscribe that is)
#For the next step I will probably store all the config in an ini file and the IP's in a text file then I can compare the IP's and only
#update the spreadsheet if they have changed.

import time
import datetime
import gspread
import os
import sys
import subprocess
import traceback


email 		= 'alexman.hdz@gmail.com'   #this is your full gmail address
password 	= 'zwtvwlypujxfmttg'        #this is your gmail password
spreadsheet_name= "SmartRasPi Docs"
worksheet_name 	= "IP_dev01"

IP_WEBSITE 	= "http://myip.xname.org"   #this is the url i am using to get the public IP

time.sleep(120)

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


def getip(): #Gets the local IP using the hostname -I method
   command = "hostname -I"
   proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
   output = proc.stdout.read()
   output = output.replace("\n","")
   return output
   
def getpubip(): #Gets the public IP by doing a get of the webpage below
   url = "myip.xname.org:80"
   import httplib, urllib
   headers = {"Content-type": "HTML"}
   params = ''
   conn = httplib.HTTPConnection(url)
   conn.request("GET", "/")
   response = conn.getresponse()
   message = response.status, response.reason
   message = str(message) 
   #print message #print http responce for debugging
   ip = response.read()
   ip = ip.replace("\n","") #get rid of new line character (may not be necessary)
   return ip
   
def uptime(): #gets uptime load average etc could split it out easily if needed it is comma seperated
   command = "uptime"
   proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
   output = proc.stdout.read()
   output = output.replace("\n","") #get rid of new line character (may not be necessary)
   return output


def main():
   publip=getpubip() # it doesnt seem to like it if I try to return the output directly into the dictionary so I stick in a variable first
   loclip=getip()
   uptim=uptime()

   values = [time.strftime('%m/%d/%Y'),
	     time.strftime('%H:%M:%S'),
	     publip,
             loclip,
             uptim,
  	     "Restart"]


   #print values #print for debugging
   worksheet.append_row(values)


if __name__ == '__main__':
   #while True:
      try:
         main()
         time.sleep(1)
      except:
         print "Insert Row Failed!"
         print '-'*60
         print traceback.format_exc()
         print '-'*60
         sys.exit()
