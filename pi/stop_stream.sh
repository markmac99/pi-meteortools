#!/bin/bash

if [ "$1" == "" ] ; then
    rtspsrc="$(grep device ~/source/RMS/.config | awk '{print $2}')"
    cd $HOME/RMS_data/logs
else
    rtspsrc="$(grep device ~/source/Stations/$1/.config | awk '{print $2}')"
    cd $HOME/RMS_data/$1/logs
fi

ffmpid=$(ps -ef | grep ffmpeg | grep youtube |awk '{print $2}')
echo "ffmpeg running as pid $ffmpid, killing it"

kill -9 $ffmpid
echo "done"
