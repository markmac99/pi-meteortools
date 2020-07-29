#!/bin/bash

# Monitor the RMS log for detection
dt=`date +%Y%m%d`
logf=`ls -1tr ~/RMS_data/logs/log*.log | tail -1 | head -1`
capdir=`grep "Data directory" $logf | awk '{print $6}'`
if [ "$capdir" = "" ] 
then
  while true ; do
    dt=`date +%Y%m%d`
    capdir=`ls -ld /home/pi/RMS_data/CapturedFiles/*${dt}*`  
    if [ "$capdir" != "" ]; then
      break
    fi
    echo waiting for capdir to be created
    sleep 30
  done
fi 

echo checking $logf
tail -Fn0 $logf | \
  while read line ; do
    echo "$line" | grep "meteors:"| egrep -v ": 0"
    if [ $? = 0 ]
    then
     ffname=`echo "$line" | grep "meteors:"| egrep -v ": 0"| awk '{print $4}'`
     echo   "found a meteor $ffname..."
     logger "found a meteor $ffname..."
     ~/ukmon/liveUploader.sh $capdir/$ffname
    fi
    #logger 'watchdog continuing...'
  done
  logger 'watchdog exiting...'

