#!/usr/bin/python
import commands
import os
import sys
import time
import os.path

import smart_timer_lib


##########################################################################
#main
smart_timer_lib.checkLastRun() # print time.time()
smart_timer_lib.checkWeekSkip()
smart_timer_lib.checkWind()
#smart_timer_lib.checkFreezeConditions()
smart_timer_lib.checkRain()
smart_timer_lib.checkRainChance()
smart_timer_lib.runCycle()

#todo
#call script to schedule next cycle cron job, based on postponing a day, or running on schedule

print 'thisIsTheEnd.'

 
"""
###
# My vars
nanotime=`date +'%s'`
mydate=`date`
currentWind=0
currentHumidity=0
sunrise=0
sunset=0
codeToday=0
codeTomorrow=0
lowestTemp=0
lowToday=0
highestTemp=0
rainChanceToday=0
windToday=0
avgWinds=0
aveRainChance=0
accumulatedRain=0


##NOTES
Type:
manual test, run for 3 seconds, exit

Type:
Scheduled cycle

If it rained at least .5 inches in the last 72 hours, exit

if there is a >50% chance of rain within 48 hours, exit

if there is a >80% in 72 hrs, exit

if the current wind is 20mph or higher, postpone cycle 24 hrs, exit

if the lowToday is < 34, postpone cycle 24 hrs, exit

if there is a freeze expected later in the week, postpone cycle, exit

else, run as scheduled.

###
"""
