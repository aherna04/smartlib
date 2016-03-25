#!/bin/bash

#zones shoule be 90 for light soak
cd /home/pi/weathertest

/home/pi/weathertest/run_zone.py 0 60
#110
sleep 8

/home/pi/weathertest/run_zone.py 1 60
#110
sleep 8

/home/pi/weathertest/run_zone.py 2 60
#90
sleep 8

/home/pi/weathertest/run_zone.py 3 60
#80
sleep 2


