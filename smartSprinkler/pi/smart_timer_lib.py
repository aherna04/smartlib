#!/usr/bin/python
import commands
import os
import sys
import time
import os.path

import smart_timer_config

###############
#import local params
################
zone=smart_timer_config.zone
zoneTimes=smart_timer_config.zoneTimes

################
#RPI HW
################
rpi=1

################
#general params
################
rainAccThreshold=.50
rainChanceTodayThreshold=50
rainChanceTomorrowThreshold=50
rainChanceAfterTomorrowThreshold=60
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
myLogFile=commands.getoutput('ls -1rt logs/*.log | tail -1')
myfile=open(myLogFile)

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
    classvars.myZone=(classvars.myZone+1)%zone
    myoutput=commands.getoutput('echo %s > currentZone' % classvars.myZone)
    #print "current zone now:", classvars.myZone
   

##########################################################################
#Enable the relay GPIO 21
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
	startRelay()
	time.sleep(2.5)
	stopRelay()
	time.sleep(3)
	updateZone();


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
	startRelay()
	time.sleep(3)
	stopRelay()
	time.sleep(2)
	updateZone();


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
        startRelay()
        print ' runtime', zoneTimes[classvars.myZone]
        print ' doing other things, etc'
        print ' like log time, etc'
        time.sleep(zoneTimes[classvars.myZone])
        stopRelay()
	time.sleep(2)
        updateZone();


    print "End : %s" % time.ctime()
    print 'cycle completed'
    print '---------------------------'
    print '------Cycle Completed------'
    print '---------------------------'
 else:
    print '---------------------------'
    print '-----Skipping Cycle--------'
    print '---------------------------'

