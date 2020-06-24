#!/bin/bash
#
# A script to run some postprocessing on the Pi. 
# Schedule this to run from a crontab during the day when the pi is
# otherwise idle, as it will conflict with RMS otherwise
#
# note: if you have mmsmtp installed this script will also email you 
# a daily summary of any detections
#
source ~/vRMS/bin/activate
export DISPLAY=:0.0
srcdir=`dirname $0`
source $srcdir/config.ini

curdir=`ls -1 ~/RMS_data/CapturedFiles/ | tail -1`
capdir=/home/pi/RMS_data/CapturedFiles/${curdir}
arcdir=/home/pi/RMS_data/ArchivedFiles/${curdir}
curdt=`echo $curdir |  sed 's/_/ /g' | awk '{ print $2 }'`
pushd /home/pi/source/RMS
export PATH=$PATH:/usr/local/bin

# Create a stack and convert the FITS files to a JPGs
python -m Utils.StackFFs -x -b $arcdir jpg
python -m Utils.BatchFFtoImage $arcdir jpg
# optionally generate an MP4 video of each capture.  
# the latter requires an extension to RMS that I have written but which is
# not yet integrated 
if [ -f Utils/GenerateMP4s.py ] ; then 
    python -m Utils.GenerateMP4s $arcdir
fi
# generate a whole-night timelapse and move it to the ArchivedFiles folder
python -m Utils.GenerateTimelapse $capdir
popd
mv $capdir/UK*.mp4 $arcdir

# optionally, send the timelapse to your youtube channel
# Configuring a channel is explained in the Youtube API docs 
# and so i won't explain here
#
fn=`ls -1 $arcdir/UK*.mp4`
tod=`basename $arcdir | cut -c8-15`
if [[ -f ${srcdir}/sendToYoutube.py && -f ${srcdir}/token.pickle ]] ; then 
    /home/pi/vRMS/bin/python ${srcdir}/sendToYoutube.py "Meteorcam timelapse for $tod" $fn
fi

# if msmtp is installed, try to send an email summary of the night
if [ -f /usr/bin/msmtp ] ; then 
    echo From: pi@`hostname` > /tmp/message.txt
    echo To: $MAILRECIP >> /tmp/message.txt
    mc=`grep meteors: ~/RMS_data/logs/log*${curdt}*.log* | grep -v ": 0" | wc -l | awk '{print $1}'`
    if [ $mc -gt 0 ] ; then
        echo Subject: `hostname`: $curdt: $mc meteors found >> /tmp/message.txt    
        grep meteors: ~/RMS_data/logs/log*${curdt}*.log* | grep -v ": 0" | awk '{printf("%s %s %s %s\n", $4, $5,$6,$7)}' >> /tmp/message.txt
    else
        echo Subject: `hostname`: $curdt: No meteors found >> /tmp/message.txt    
    fi
    /usr/bin/msmtp -t  < /tmp/message.txt
    rm -f /tmp/message.txt
fi

# keep a record of how many FF files were created each night
# this is to monitor for lost data

curdt=`basename $capdir | cut -d "_" -f 2`

noffs=`ls -1 $capdir/FF*.fits | wc -l | awk '{print $1}'`
ffhrs=`awk -v var1=$noffs 'BEGIN {print ( var1 / 351.56 ) }'`
hours=`ls -1tr ~/RMS_data/logs/log_${curdt}* | while read i ; do grep Waiting $i| grep record ; done | awk '{print $10}' | uniq`
grabs=`ls -1tr ~/RMS_data/logs/log_${curdt}* | while read i ; do grep Grabbing $i ; done | wc -l`

echo $curdt $hours $noffs $ffhrs $grabs >> /home/pi/RMS_data/logs/ffcounts.txt