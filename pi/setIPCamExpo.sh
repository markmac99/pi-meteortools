#!/bin/bash
# Copyright (C) Mark McIntyre
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $HOME/vRMS/bin/activate
source $here/config.ini >/dev/null 2>&1

if [ $# -lt 3 ] ; then
  echo "usage setIPCamExpo.sh DAY|NIGHT {ipaddress} {camid}"
  exit 1
fi
IPCAMADDR=$2
CAMID=$3

logger  -s -t setIPCamExpo "Setting exposure for $1. Camera is $IPCAMADDR, gain is $NIGHTGAIN"
python3 $here/setExpo.py $IPCAMADDR $1 $CAMID $NIGHTGAIN 
