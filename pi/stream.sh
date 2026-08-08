#!/bin/bash

# Script to stream from a camera to Youtube using ffmpeg
# 
# NB: you must configure and start the Live Stream on Youtube before running this script.
# If you intend to run over multiple days, you'll need to restart the Livestream in Youtube Studio each day 
# by going to your channel, selecting Youtube Studio, then selecting Go Live from the Create menu top-right. 
#
# Obtain your key by clicking the copy button at the top-right corner of the Livestream window in YT Studio's livestreaming page. 
#
ytkey=YOURKEYHERE

if [ "$1" == "" ] ; then
    	if [ -d ~/source/Stations ] ; then
		statid=$(ls -1 ~/source/Stations | head -1)
    	else
		statid-$(grep stationID ~/source/RMS/.config | awk '{print $2}')
    	fi
else
    	statid=$1
fi

if [[ "$statid" == "XX0001" || "$statid" == "" ]] ; then 
  	echo "Can't stream default or null station $statid "
  	exit
fi

if [ ! -f ~/source/Stations/$statid/.config ] ; then 
	echo "camera $statid not present here"
	exit
fi 

rtspsrc="$(grep device ~/source/Stations/$statid/.config | awk '{print $2}')"
LOGDIR=$HOME/RMS_data/$statid/logs

if [ "$rtspsrc" == "" ] ; then
        rtspsrc="$(grep device ~/source/RMS/.config | awk '{print $2}')"
        LOGDIR=$HOME/RMS_data/logs
fi 
cd $LOGDIR

echo "starting reading $statid from $rtspsrc to $ytkey"

/usr/bin/ffmpeg -use_wallclock_as_timestamps 1 -f lavfi -i anullsrc -rtsp_transport tcp -i $rtspsrc -tune zerolatency -vf "drawtext=fontsize=30:text='%{localtime}':fontcolor=white@0.8:x=5:y=(h-text_h-5)" -c:a aac -strict experimental -loglevel debug -f flv rtmp:/a.rtmp.youtube.com/live2/$ytkey > $LOGDIR/ffmpeg_stream.log 2>&1 &

