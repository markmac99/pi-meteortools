#!/bin/bash

# monitor the logfile and if the capture process stops, restart it
# Run this at boot time with cron but wait for RMS to start up
#
# @reboot sleep 600 && /home/pi/mjmm/RMS_Pi4Monitor.sh > /dev/null 2>&1
#
logger 'RMS pi4 watchdog process starting'
export DISPLAY=:0.0
sleepint=120

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
    grep "Starting capture" $fn
    if [ $? -eq 0 ] ; then 
      # capture has started but may also have finished
      # we need to check this as some postprocessing actions can take many minutes
      grep Stopping $fn
      if [ $? -eq 1 ] ; then
        # ok capture started but has not completed and has probably stalled
        logger 'RMS_Pi4Watchdog: RMS stopped acquisition'

        # Restart RMS. taking care not to kill other python apps
        ps -ef | grep RMS_ | egrep -v "watch|data|grep"|awk '{print $2}' | while read i
        do
          kill $i
        done
        logger 'RMS_Pi4Watchdog: killed RMS'
        sleep 5

        cd ~/source/RMS
        lxterminal -e Scripts/RMS_StartCapture.sh -r  & 
        logger 'RMS_Pi4Watchdog: restarted RMS...'


        if [ -d ~/source/ukmon-pitools ] ; then
          cd ~/source/ukmon-pitools
          ps -ef | grep liveMonitor | egrep -v "grep"|awk '{print $2}' | while read i
          do
            kill $i
          done
          sleep 300
          lxterminal -e ./liveMonitor.sh >> /home/pi/RMS_data/logs/ukmon-live.log 2>&1  &
          logger 'RMS_Pi4Watchdog: restarted ukmon liveMonitor...'
        fi

        cd /home/pi/RMS_data/logs
        logger 'RMS_Pi4Watchdog: continuing...'
      else
        logger 'RMS_Pi4Watchdog: Capture stopped normally'
      fi
    else
      logger 'RMS_Pi4Watchdog: Capture not started yet'
    fi
  else
      logger 'RMS_Pi4Watchdog: Capture running ok'
  fi

  sleep $sleepint
done
logger 'watchdog exiting...'

exit 0

