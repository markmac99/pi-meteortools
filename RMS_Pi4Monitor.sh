#!/bin/bash

# monitor the logfile and if the capture process stops, restart it
logger 'RMS pi4 watchdog process starting'
export DISPLAY=:0.0

# Run this at boot time with cron but wait for RMS to start up
#
# @reboot sleep 600 && /home/pi/mjmm/RMS_Pi4Monitor.sh > /dev/null 2>&1
#
logger 'RMS_Pi4Watchdog: starting checks'

cd /home/pi/RMS_data/logs
dead="no"
while [ "$dead" != "yes" ]
do
  # find most recent logfile then check when it last updated
  fn=`ls -1tr log* | tail -1`
  sts=`find . -name $fn -mmin +10 -ls | wc -l`

  if [ $sts -ne 0 ] ; then  
    # log file is more than ten minutes old
    # check that we're not still waiting for capture to start
    grep Starting $fn
    if [ $? -eq 0 ] ; then 
      # capture has started but may also have finished
      # we need to check this as some postprocessing actions can take many minutes
      grep Stopping $fn
      if [ $? -eq 1 ] ; then
        # ok capture started but has not completed and has probably stalled
        logger 'RMS_Pi4Watchdog: RMS stopped acquisition'
        echo killall python
        logger 'RMS_Pi4Watchdog: killed python'
        sleep 5
        rmspid=`ps -ef | grep RMS_StartCapture.sh | grep -v grep | awk '{print $2}'`
        logger 'RMS_Pi4Watchdog: rms pid is $rmspid'
        echo kill -9 $rmspid
        logger 'RMS_Pi4Watchdog: killed rms bash script'
        sleep 5
        cd ~/source/RMS
        echo lxterminal -e Scripts/RMS_StartCapture.sh -r  & 
        logger 'RMS_Pi4Watchdog: restarted RMS...'
        cd ~ukmon
        echo killall liveMonitor.sh
        sleep 5
        echo lxterminal -e liveMonitor.sh  
        logger 'RMS_Pi4Watchdog: restarted liveMonitor...'
        cd /home/pi/RMS_data/logs
        logger 'RMS_Pi4Watchdog: continuing...'
      else
        echo Capture stopped so no need to restart script
      fi
    else
      echo Capture not started yet so no need to restart script
    fi
  else
      echo Capture running ok so no need to intervene
  fi

  sleepint=20
  sleep $sleepint
done
logger 'watchdog exiting...'

exit 0

