#!/bin/bash
cd /home/pi/smartlib/smartSprinkler

./run_zone.py 0 400
# 240
sleep 8

./run_zone.py 1 500
#350
sleep 8

./run_zone.py 2 400
#350
sleep 8

./run_zone.py 3 300
sleep 2


