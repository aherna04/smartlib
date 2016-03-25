#!/bin/bash
cd /home/pi/weathertest

/home/pi/weathertest/run_zone.py 0 250
sleep 8

/home/pi/weathertest/run_zone.py 1 350
