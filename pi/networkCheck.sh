#!/bin/bash
# Copyright (C) Mark McIntyre
#
# Script to restart wifi if the Pi loses connection
#
# TO USE THIS SCRIPT
# Create a folder /home/pi/mjmm and save this file into it 
# Open a Terminal window and type the following
#   cd ~/mjmm
#   chmod 755 ./networkCheck.sh
#   crontab -e
# if you're prompted to select an Editor, choose nano.
#
# This will open the list of scheduled jobs (crontab) in an editor.
# Copy/paste the following line at the bottom of the file:
# @reboot sleep 60 && /home/pi/mjmm/networkCheck.sh > /home/pi/RMS_data/logs/networkCheck-`date +\%Y\%m\%d`.log 2>&1
# Press Ctrl-X then Y to exit and save.
# Now reboot the Pi. The job will now be scheduled. 
# To check that it is scheduled, look in /home/pi/RMS_data/logs for a file named networkCheck.... 

logger -s -t networkCheck "starting"

while [ "$gwaddr" == "" ] ; do 
    gwaddr=$(ip r | grep default | awk '{print $3}') 
    sleep 5 
done

logger -s -t networkCheck "using $gwaddr to test network"
while true
do
    ping -c 1 $gwaddr  > /dev/null 2>&1
    x=$?
    sleep 30
    ping -c 1 $gwaddr  > /dev/null 2>&1
    y=$? 
    if [[ $x -ne 0 && $y -ne 0 ]] ; then 
        logger -s -t networkCheck "wifi went off"
        sudo ifconfig wlan0 down
        sudo ifconfig wlan0 up
        sleep 60
        ping -c 1 $gwaddr  > /dev/null 2>&1
        y=$? 
        if [ $y -ne 0 ] ; then 
            logger -s -t networkCheck "wifi still off, rebooting"
            sudo reboot
        fi
    fi
    sleep 60
done  

