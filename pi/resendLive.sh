#!/bin/bash

cd $HOME/source/ukmon-pitools

if [ $# -lt 1 ] ; then echo "usage: ./resendLive.sh yyyymmdd" ; exit ; fi
dt=$1
logfile=$(ls -1 ~/RMS_data/logs/ukmonlive*${dt}_12*)
for log in $logfile ; do
    capdir=$(grep capture $logfile  | awk '{print $8}')
    if [ -z $capdir ] ; then 
        capdir=$(ls -1d ~/RMS_data/CapturedFiles/*${dt}*)
    fi
    ffs=$(grep uploading $logfile  | awk '{print $5}')
    for ff in $ffs ; do
        python ./sendToLive.py $capdir $ff
    done 
done
