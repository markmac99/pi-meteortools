#!/bin/bash

if [ "$1" == "" ] ; then
    rtspsrc="$(grep device ~/source/RMS/.config | awk '{print $2}')"
    cd $HOME/RMS_data/logs
else
    rtspsrc="$(grep device ~/source/Stations/$1/.config | awk '{print $2}')"
    cd $HOME/RMS_data/$1/logs
fi

# rtspsrc="rtsp://192.168.1.21:554/user=admin&password=&channel=1&stream=0.sdp"
ytkey=1434-e6kc-86uz-qmce-855h #0kew-3dad-tg4r-2mue-acry

echo "starting reading from $rtspsrc to $ytkey"
/usr/bin/ffmpeg -use_wallclock_as_timestamps 1 -f lavfi -i anullsrc -rtsp_transport tcp -i $rtspsrc -tune zerolatency -c:v copy -c:a aac -strict experimental -loglevel debug -f flv rtmp:/a.rtmp.youtube.com/live2/$ytkey > $HOME/RMS_data/logs/ffmpeg_stream.log 2>&1 &

