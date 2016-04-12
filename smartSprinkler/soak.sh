#!/bin/bash
cd /home/pi/smartlib/smartSprinkler

./run_zone.py 0 240
sleep 8

./run_zone.py 1 240
sleep 8

./run_zone.py 2 180
sleep 8

./run_zone.py 3 180
sleep 2


