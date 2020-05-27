#!/bin/bash
#
# Run this every 10 mins from crontab to be alerted in near realtime to events
# 
# REQUIRES ssmtp - a simple mailer which can be installed with apt-get
#
# set this to the address to recieve notifications
MAILRECIP=youremail@here

if [ ! -f /usr/sbin/ssmtp ] ; then
   echo ssmtp not installed, cannot continue
   exit
fi

here=`dirname $0`
cd ${here}/eventlog

hr=`date +%H`
if [ $hr -lt 16 ] ; then
  dt=`date -d '1 days ago' +%Y%m%d`
else
  dt=`date +%Y%m%d`
fi
fnam=${dt}.txt

grep meteors: /home/pi/RMS_data/logs/*$dt*.log | awk -F ' ' '{printf("%s %s %s \n", $4, $6, $7) }' | grep -v ": 0" > latest.txt
diff $fnam latest.txt
if [[ -f $fnam && $? -ne 0 ]] ; then
  echo From: meteorpi@home > message.txt
  echo To: $MAILRECIP >> message.txt
  echo Subject: $dt: new meteors found >> message.txt
  diff $fnam latest.txt >> message.txt
  /usr/sbin/ssmtp -t  < message.txt
  #rm -f message.txt
  cp latest.txt $fnam
else 
  touch $fnam
fi

