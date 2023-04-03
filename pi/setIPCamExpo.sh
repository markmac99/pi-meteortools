#!/bin/bash
# Copyright (C) Mark McIntyre
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $HOME/vRMS/bin/activate
source $here/config.ini >/dev/null 2>&1
pip install python-crontab

cd $RMSDIR
if [ "$1" == "" ] ; then
  echo "usage setIPCamExpo.sh DAY|NIGHT {ipaddress}"
  exit 1
fi
if [ "$2" == "" ] ; then 
  IPCAMADDR=$(grep device .config  |awk -F "rtsp://" '{ print $2 }' | awk -F: '{print $1 }' | uniq)
else
  IPCAMADDR=$2
fi

logger  -s -t setIPCamExpo "Setting exposure for $1. Camera is $IPCAMADDR, gain is $NIGHTGAIN"
python3 $here/SetExpo.py $IPCAMADDR $1 $NIGHTGAIN
