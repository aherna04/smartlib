#!/bin/bash
cd /home/pi/smartlib/smartSprinkler

./run_zone.py 0 600
# 240
sleep 8

./run_zone.py 1 1000
#350
sleep 8

./run_zone.py 2 900
#350
sleep 8

./run_zone.py 3 500
#280
sleep 2


