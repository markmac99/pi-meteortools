#!/bin/bash
#
# Run this from crontab to check for meteors in last night's
# log then email yourself if there is something of interest
# 
# REQUIRES msmtp - a simple mailer which can be installed with 
#  sudo apt-get install msmtp msmtp-mta
#
# set this to the address to recieve notifications
MAILRECIP=youremail@here

if [ ! -f /usr/bin/msmtp ] ; then
   echo msmtp not installed, cannot continue
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
hn=`hostname`

mcount=`wc -l $fnam | awk '{print $1}'`
if [ ${mcount} -gt 0 ] ; then
   numm=${mcount}
else
   numm="no"
fi 
echo From: pi@${hn} > /tmp/message.txt
echo To: $MAILRECIP >> /tmp/message.txt
echo Subject: $hn: $dt: $mcount meteors found >> /tmp/message.txt
echo $tod there were $mcount meteors found by $hn >> /tmp/message.txt

/usr/bin/msmtp -t  < /tmp/message.txt
rm -f /tmp/message.txt

