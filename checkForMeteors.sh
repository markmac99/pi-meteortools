#!/bin/bash
#
# Run this from crontab to check for meteors in last night's
# log then email yourself if there is something of interest
# 
# REQUIRES ssmtp - a simple mailer which can be installed with apt-get
#
# set this to the address to recieve notifications
MAILRECIP=mark.jm.mcintyre@cesmail.net

if [ ! -f /usr/sbin/ssmtp ] ; then
   echo ssmtp not installed, cannot continue
   exit
fi
rm -f /tmp/metcheck.txt
find /home/pi/RMS_data/logs/ -mtime -1 -type f -name log* -exec ls -1 {} \; | while read i; do grep meteors: $i | egrep -v ": 0" >> /tmp/metcheck.txt ; done
mcount=`wc -l /tmp/metcheck.txt | awk '{print $1}'`
echo From: meteorpi@home > /tmp/message.txt
echo To: $MAILRECIP >> /tmp/message.txt
if [ ${mcount} -gt 0 ] ; then
   echo Subject: $mcount meteors found >> /tmp/message.txt
   echo $mcount meteors found >> /tmp/message.txt
else
   echo Subject: No meteors found >> /tmp/message.txt
   echo nothing to report today >> /tmp/message.txt
fi
echo "." >> /tmp/message.txt
/usr/sbin/ssmtp -t  < /tmp/message.txt
rm -f /tmp/metcheck.txt /tmp/message.txt

