#!/usr/bin/python
import commands
import os
import sys
import time
import os.path

import smart_timer_config
#smartSprinklerHome
workingDir="/home/pi/smartlib/smartSprinkler"
os.chdir(workingDir)

###############
#import local params
################
zone=smart_timer_config.zone
zoneTimes=smart_timer_config.zoneTimes

################
#RPI HW
################
rpi=smart_timer_config.rpi

print "HW"
print rpi
################
#general params
################
rainAccThreshold=.70

#--weather.com - no longer supported --#
#rainChanceTodayThreshold=50
#rainChanceTomorrowThreshold=50
#rainChanceAfterTomorrowThreshold=60

weathercodes = {1,2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18,35,37,38,39,40,41,42,43,45,46,47}

windTodayThreshold=20
freezeThreshold=35

weekSkipThreshold=2.5
daySeconds=86400
weekSkip=daySeconds*7

myoutput=0

class classvars: pass
classvars.run=1

nanotime=commands.getoutput("date +'%s'")

#read current zone
classvars.myZone=int(commands.getoutput('cat currentZone'))


# read latest Log
#TOOD: add create logs folder if missing
try:
	myLogFile=commands.getoutput('ls -1rt ' + workingDir + '/logs/*.log | tail -1')
	myfile=open(myLogFile)
except IOError:
	print "create logs folder"
	exit(1)


# parse log file
myvars = {}
with myfile:
    for line in myfile:
        name, var = line.partition(":")[::2]
        myvars[name.strip()] = var.strip()


def checkLastRun():
    print '---------------------------'
    print '-----Checking Stats--------'
    print '---------------------------'
    print "Last Checked:"
    print myvars["mydate"]
    print "Time Now : %s" % time.ctime()

##########################################################################
#write active zone to file to track state
def updateZone():
    #TODO
    #SKIP IF rpi == 0
    classvars.myZone=(classvars.myZone+1)%zone
    myoutput=commands.getoutput('echo %s > currentZone' % classvars.myZone)
    #print "current zone now:", classvars.myZone
   

##########################################################################
#Enable the relay GPIO 17
def startRelay():
    print "-START RELAY:" 
    if rpi:
      commands.getoutput('echo 1 > /sys/class/gpio/gpio17/value')
      myoutput=commands.getoutput('cat /sys/class/gpio/gpio17/value')

      print myoutput

##########################################################################
#Disable the relay GPIO 21
def stopRelay():
    print "-STOP RELAY:" 
    if rpi:
       commands.getoutput('echo 0 > /sys/class/gpio/gpio17/value')
       myoutput=commands.getoutput('cat /sys/class/gpio/gpio17/value')

       print myoutput

##########################################################################
#check relay - isRunning 1 yes, 0 no
def isRunning():
       myoutput=commands.getoutput('cat /sys/class/gpio/gpio17/value')

       return myoutput

##########################################################################
#Are we skipping for a week? 
def checkWeekSkip():
    if os.path.isfile("week.skip"):
       weekCheck=commands.getoutput('cat week.skip')
       print "Found week.check file... are we in skip window?"
       print "   currentTime: ",nanotime 
       print "   skip cycle : ",weekCheck
       if nanotime < weekCheck:
          print "   ***Still in skip window, cancel***"
	  classvars.run=0
       else:
          print "   Skip window expired... removing week.check file"
          commands.getoutput('rm week.skip')
       
    else: 
        print "Not in skip window..."



##########################################################################
#Rain amount check
def checkRain():
    if float(myvars["accumulatedRain"]) > rainAccThreshold:
        print myvars["accumulatedRain"],':**Sufficient rain, cancel.**'
        classvars.run=0
    else: 
        print myvars["accumulatedRain"],':Not enough rain'

##########################################################################
#check rain chance
def checkRainChance():
    if int(myvars["rainChanceToday"]) >= rainChanceTodayThreshold:
        print myvars["rainChanceToday"],':**Rain expected today, cancel.**'
        classvars.run=0
    elif int(myvars["rainChanceTomorrow"]) >= rainChanceTomorrowThreshold:
        print myvars["rainChanceTomorrow"],':**Heavy rain expected tomorrow, cancel.**'
        classvars.run=0
    elif int(myvars["rainChanceAfterTomorrow"]) >= rainChanceAfterTomorrowThreshold:
        print myvars["rainChanceAfterTomorrow"],':**Heavy rain expected after tomorrow, cancel.**'
        classvars.run=0
    else:
        print myvars["rainChanceToday"],myvars["rainChanceTomorrow"],myvars["rainChanceAfterTomorrow"], ':Not enough rain expected.'


##########################################################################
#check rain chance  for light rain, check rain totals. If rain totals are 0, then do not skip
#TODO - feature upgrade
def yahooCodeCheck(code):
	if code == 1 or code == 2 or code ==3 or code==4 or code==5 or code==5 or code==6 or code==7 or code==8:
        	print ':**Sufficient rain or storms, cancel.**'
        	classvars.run=0
	elif code==10 or code==11 or code==12 or code==13 or code==14 or code==15 or code==16 or code==17 or code==18:
        	print ':**Sufficient rain or showers, cancel.**'
        	classvars.run=0
	elif code==35 or code==37 or code==38 or code==39:
        	print ':**Sufficient rain, cancel.**'
        	classvars.run=0
	elif code==40 or code==41 or code==42 or code==43 or code==45 or code==46  or code==47:
        	print ':**thunderstorms, cancel.**'
        	classvars.run=0
	else: 
            print  ':Not enough rain expected'

##########################################################################
#check yahoo codes
def checkYahooCodes():
    print 'today:', myvars["conditionToday"], 
#TODO
#    yahooCodeCheck(int(myvars["codeToday"]))
    print
    print 'tomorrow: ', myvars["conditionTomorrow"], 
#TODO
#    yahooCodeCheck(int(myvars["codeTomorrow"]))
    print
    print 'aftertomorrow: ', myvars["conditionAfterTomorrow"], 
#TODO
#    yahooCodeCheck(int(myvars["codeAfterTomorrow"]))
    print

##########################################################################
#check wind conditions
def checkWind():
    if int(myvars["windToday"]) > windTodayThreshold:
        print myvars["windToday"],':**High winds, postpone.**'
        classvars.run=0
    else: 
        print myvars["windToday"],':Not too windy'

##########################################################################
#check freeze temps
def checkFreezeConditions():
    if int(myvars["lowToday"]) < freezeThreshold:
        print myvars["lowToday"],':**Freeze expected today, cancel.**'
        classvars.run=0
    elif int(myvars["lowestTemp"]) < freezeThreshold:
        print myvars["lowestTemp"],':**Freeze expected this week, cancel.**'
        classvars.run=0
    else:
        print myvars["lowToday"],myvars["lowestTemp"],':Freeze not expected'



##########################################################################
#skip ahead one cycle
def nextCycle():
	updateZone();
	startRelay()
	time.sleep(5)
	stopRelay()
	time.sleep(8)


##########################################################################
#runTestCycle - run each zone for 3 seconds, waiting 2 between zones
def runTestCycle():
    print '---------------------------'
    print '-----Running Test Cycle---------'
    print '---------------------------'
    print "Start : %s" % time.ctime()

    for i in range(zone):
	print 'loop:', i, ' zone:', classvars.myZone
	print "sleep timer", zoneTimes[classvars.myZone]
	updateZone();
	startRelay()
	time.sleep(5)
	stopRelay()
	time.sleep(8)


    print "End : %s" % time.ctime()
    print 'cycle completed'
    print '---------------------------'
    print '------Cycle Completed------'
    print '---------------------------'


##########################################################################
#RunCycle - runs a full wet cycle, each zone has it's own run timer
#         - waiting 2 seconds between zones
def runCycle():
 if classvars.run==1:
    print '---------------------------'
    print '-----Running Cycle---------'
    print '---------------------------'
    print "Start : %s" % time.ctime()
    print 'setting timer, sleeping...'

    for i in range(zone):
	print 'loop:', i, ' zone:', classvars.myZone
	updateZone();
        startRelay()
        print ' runtime', zoneTimes[classvars.myZone]
        print ' doing other things, etc'
        print ' like log time, etc'
        time.sleep(zoneTimes[classvars.myZone])
        stopRelay()
	time.sleep(8)


    print "End : %s" % time.ctime()
    print 'cycle completed'
    print '---------------------------'
    print '------Cycle Completed------'
    print '---------------------------'
 else:
    print '---------------------------'
    print '-----Skipping Cycle--------'
    print '---------------------------'

