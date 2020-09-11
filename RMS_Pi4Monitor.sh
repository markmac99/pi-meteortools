#!/bin/bash

# monitor the logfile and if the capture process stops, restart it
logger 'RMS pi4 watchdog process starting'
export DISPLAY=:0.0

# need to wait in case RMS is still starting up and the logfile is not
# yet available
#sleep 180
echo starting checks

cd /home/pi/RMS_data/logs
dead="no"
while [ "$dead" != "yes" ]
do
  fn=`ls -1tr log* | tail -1`
  logf=`find . -name $fn -mmin +10 -ls`
  dayt=`wc -l $fn | awk '{print $1}'`
  if [[ "$logf" !=  "" && $dayt -gt 30 ]] ; then
    finished=`grep thumbnails $fn`
    if [ "$finished" != "" ] ; then
        logger 'RMS Pi4 watchdog process finished cleanly'
        exit 0
    fi
    logger 'RMS Pi4 watchdog RMS stopped acquisition'
    killall python
    logger 'killed python'
    sleep 5
    rmspid=`ps -ef | grep RMS_StartCapture.sh | grep -v grep | awk '{print $2}'`
    logger 'rms pid is $rmspid'
    kill -9 $rmspid
    logger 'killed rms bash script'
    sleep 5
    cd ~/source/RMS
    lxterminal -e Scripts/RMS_StartCapture.sh -r  & 
    logger 'RMS Pi4 watchdog restarted RMS...'
    cd ~ukmon
    killall liveMonitor.sh
    sleep 5
    lxterminal -e liveMonitor.sh  
    logger 'RMS Pi4 watchdog restarted liveMonitor...'
    cd /home/pi/RMS_data/logs
    logger 'RMS Pi4 watchdog continuing...'
  fi
  sleepint=20
  sleep $sleepint
done
logger 'watchdog exiting...'

exit 0

