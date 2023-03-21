#!/bin/bash
#
# A script to track the number of images captured each night
#
srcdir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

curdir=`ls -1 $HOME/RMS_data/CapturedFiles/ | tail -1`
capdir=$HOME/RMS_data/CapturedFiles/${curdir}
curdt=`echo $curdir |  sed 's/_/ /g' | awk '{ print $2 }'`

noffs=`ls -1 $capdir/FF*.fits | wc -l | awk '{print $1}'`
ffhrs=`awk -v var1=$noffs 'BEGIN {print ( var1 / 351.56 ) }'`
hours=`ls -1tr $HOME/RMS_data/logs/log_${curdt}* | while read i ; do grep Waiting $i| grep record ; done | awk '{print $11}' | uniq`
grabs=`ls -1tr $HOME/RMS_data/logs/log_${curdt}* | while read i ; do grep Grabbing $i ; done | wc -l`

echo $curdt $hours $noffs $ffhrs $grabs >> $HOME/RMS_data/logs/ffcounts.txt


