#!/usr/bin/python
import commands
import os
import sys
import time
import os.path

import smart_timer_lib
import smart_timer_config

##########################################################################
#main

#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)

if len(sys.argv) != 2|3:
   print "Wrong syntax: run_zone ZONE Time"
   sys.exit(0)

runTimer = 5
   
if len(sys.argv) == 3:
   runTimer = int(sys.argv[2])


param=int(sys.argv[1])
currentZone=int(smart_timer_lib.classvars.myZone)

print "     CURRENT ZONE:", currentZone
print "     Set to      :", param

### If selected zone is within the zone capacity
if param < int(smart_timer_config.zone):

   ### loop until we have the proper zone selected
   ### if it's matched, just skip out 
   while currentZone%smart_timer_config.zone != param:
      print "skipping zone: ", currentZone
      smart_timer_lib.nextCycle()
      currentZone=currentZone+1

   ### Time to run the selected zone for some time...
   print "***Running Zone***:", currentZone%int(smart_timer_config.zone)
   smart_timer_lib.startRelay()
   time.sleep(runTimer)
   smart_timer_lib.stopRelay()
   smart_timer_lib.updateZone();

else:
   print "Wrong syntax:zone must be between 0 and",smart_timer_config.zone-1




