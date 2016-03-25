#!/bin/bash
cd /home/pi/weathertest

/home/pi/weathertest/run_zone.py 0 240
sleep 8

/home/pi/weathertest/run_zone.py 1 240
sleep 8

/home/pi/weathertest/run_zone.py 2 180
sleep 8

/home/pi/weathertest/run_zone.py 3 180
sleep 2


