#!/bin/bash
#
# Run this every 10 mins from crontab to be alerted in near realtime to events
# 
# REQUIRES msmtp - a simple mailer which can be installed with 
#  sudo apt-get install msmtp msmtp-mta
#
# set this to the address to recieve notifications
MAILRECIP=youremail@here

if [ ! -f /usr/bin/msmtp ] ; then
   echo msmtp not installed, cannot send mails
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
hn=`hostname`

grep meteors: /home/pi/RMS_data/logs/*$dt*.log | awk -F ' ' '{printf("%s %s %s \n", $4, $6, $7) }' | grep -v ": 0" > latest.txt
len1=`wc -l latest.txt | awk '{print $1}'`
newl=`diff latest.txt $fnam | grep -v ">"`
isline=`echo $newl | awk '{print $1}' | cut -b1`
#dl=`echo $newl | wc -l`
if [[ $len1 -ne 0  && $isline -ne 0 ]] ; then
  echo From: meteorpi@themcintyres.dnsalias.net > message.txt
  echo To: $MAILRECIP >> message.txt
  echo Subject: $hn - $dt: new meteors found >> message.txt
  evt=`echo $newl | awk '{printf("%s %s %s\n", $3, $4, $5)}'`
  echo $evt >> message.txt
  /usr/bin/msmtp -t  < message.txt
  #rm -f message.txt
  echo $evt >> $fnam
else 
  touch $fnam
fi

