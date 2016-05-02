#!/bin/bash

#zones should be 90 for light soak
cd /home/pi/smartlib/smartSprinkler

./run_zone.py 0 90
#110
sleep 8

./run_zone.py 1 110
#110
sleep 8

./run_zone.py 2 190
#90
sleep 8

./run_zone.py 3 80
#80
sleep 2


