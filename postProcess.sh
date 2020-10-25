#!/bin/bash
#
# A script to run some postprocessing on the Pi. 
# Schedule this to run from a crontab during the day when the pi is
# otherwise idle, as it will conflict with RMS otherwise
#
# note: if you have msmtp installed this script will also email you 
# a daily summary of any detections
#
export PATH=$PATH:/usr/local/bin
# required for SSL with python3
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/openssl/lib:/usr/local/openssl/lib

source ~/vRMS/bin/activate
export DISPLAY=:0.0
srcdir=`dirname $0`
source $srcdir/config.ini

curdir=`ls -1 ~/RMS_data/CapturedFiles/ | tail -1`
capdir=/home/pi/RMS_data/CapturedFiles/${curdir}
arcdir=/home/pi/RMS_data/ArchivedFiles/${curdir}
curdt=`echo $curdir |  sed 's/_/ /g' | awk '{ print $2 }'`
pushd /home/pi/source/RMS

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

#curdt=`basename $capdir | cut -d "_" -f 2`

# optionally, send the timelapse to your youtube channel
# Configuring a channel is explained in the Youtube API docs 
# and so i won't explain here
#
fn=`ls -1 $arcdir/UK*.mp4`
bn=`basename $fn`

# first check you've not already done it otherwise you will exceed your quota on youtube
grep "uploading $bn" /home/pi/RMS_data/logs/postProcess*.log > /dev/null
if [ $? -eq 0 ] ; then
    echo already uploaded $bn
    ytdone=1
else
    ytdone=0
fi 
tod=`basename $arcdir | cut -c8-15`
if [[ $ytdone -eq 0 && -f ${srcdir}/sendToYoutube.py && -f ${srcdir}/token.pickle ]] ; then 
    echo uploading $bn
    /home/pi/vRMS/bin/python ${srcdir}/sendToYoutube.py "`hostname` timelapse for $tod" $fn
fi

# upload to a website of your choice
# note that if the target host name begins with s3: then its expected to be an AWS
# S3 bucket, and the idfile is expected to contain the exported credentials.
# Otherwise its treated as a linux server to which the file can be copied 

if [ $UPLOAD -eq 1 ]; then
    ISS3=${HOST:0:3}
    YYMM=${curdt:0:6}
    STN=${curdir:0:6}
    if [ "$ISS3" == "s3:" ] ; then
        bfn=`basename $fn`
        source $IDFILE
        aws s3 cp $fn $HOST/$STN/$YYMM/$bfn
    else 
        ssh -i $IDFILE $USER@$HOST mkdir $MP4DIR/$STN/$YYMM > /dev/null 2>&1
        scp -i $IDFILE $fn $USER@$HOST:$MP4DIR/$STN/$YYMM
    fi
fi

# if msmtp is installed, try to send an email summary of the night
if [ -f /usr/bin/msmtp ] ; then 
    # test if bc is installed and install it if not
    if [ ! -f /usr/bin/bc ] ; then
        sudo apt-get install -y bc
    fi 
    echo From: pi@`hostname` > /tmp/message.txt
    echo To: $MAILRECIP >> /tmp/message.txt
    mc1=`grep "meteors\." ~/RMS_data/logs/log*${curdt}*.log* | grep detected |  awk '{print $5}'`
    mc=`echo $mc1 | sed 's/ /+/g' |  bc`
    if [ $mc -gt 0 ] ; then
        echo Subject: `hostname`: $curdt: $mc meteors found >> /tmp/message.txt    
        grep "meteors\." ~/RMS_data/logs/log*${curdt}*.log* | grep detected | awk '{printf("%s %s %s %s\n", $4, $5,$6,$7)}' >> /tmp/message.txt
    else
        echo Subject: `hostname`: $curdt: No meteors found >> /tmp/message.txt    
    fi
    /usr/bin/msmtp -t  < /tmp/message.txt
    rm -f /tmp/message.txt
fi

# keep a record of how many FF files were created each night
# this is to monitor for lost data

noffs=`ls -1 $capdir/FF*.fits | wc -l | awk '{print $1}'`
ffhrs=`awk -v var1=$noffs 'BEGIN {print ( var1 / 351.56 ) }'`
hours=`ls -1tr ~/RMS_data/logs/log_${curdt}* | while read i ; do grep Waiting $i| grep record ; done | awk '{print $11}' | uniq`
grabs=`ls -1tr ~/RMS_data/logs/log_${curdt}* | while read i ; do grep Grabbing $i ; done | wc -l`

echo $curdt $hours $noffs $ffhrs $grabs >> /home/pi/RMS_data/logs/ffcounts.txt

# backup configuration each month
mkdir $srcdir/bkp > /dev/null 2>&1
if [ `date +%d` -eq 1 ]; then 
    cp /home/pi/source/RMS/.config $srcdir/bkp/.config.`date +%Y%m`
    cp /home/pi/source/RMS/platepar_cmn2010.cal $srcdir/bkp/platepar_cmn2010.cal.`date +%Y%m`
    cp /home/pi/source/RMS/mask.bmp $srcdir/bkp/mask.bmp.`date +%Y%m`
fi
# reboot the camera. Recommended to avoid freezes and lockups
pushd /home/pi/source/RMS
echo "Rebooting the camera"
python3 -m Utils.CameraControl reboot
popd

# clear the archive dir down of anything older than 20 days
$srcdir/clearArchive.sh
