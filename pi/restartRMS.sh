#!/bin/bash

# Copyright (C) Mark McIntyre 2025

# Simple script to restart an instance of RMS

if [ $# -lt  1 ] ; then 
    echo "usage: restartRMS.sh CAMID"
    exit
fi

for pid in $(ps -ef | grep $1 | grep StartCapture | awk '{print $2}') ; do 
    kill -9 $pid 
done
SCHOME=$HOME/source/RMS/Scripts/MultiCamLinux
DATADIR=$HOME/RMS_data/$1
nohup $SCHOME/StartCapture.sh $1 2> $DATADIR/logs/console.log &
ps -ef | grep $1 | grep StartCapture