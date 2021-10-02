#!/bin/bash

# Script to restart wifi if the Pi loses connection
# crontab entry
# @reboot sleep 30 && /home/pi/mjmm/networkCheck.sh > /home/pi/RMS_data/logs/networkCheck-`date +\%Y\%m\%d`.log 2>&1
#

logger -s -t networkCheck "starting"
while true
do
    ping -c 1 192.168.1.254  > /dev/null 2>&1
    x=$?
    sleep 30
    ping -c 1 192.168.1.254  > /dev/null 2>&1
    y=$? 
    if [[ $x -ne 0 && y -ne 0 ]] ; then 
        logger -s -t networkCheck "wifi went off"
        sudo ifconfig wlan0 down
        sudo ifconfig wlan0 up
    fi
    sleep 60
done  

