#!/bin/bash
# Copyright (C) Mark McIntyre
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $HOME/vRMS/bin/activate
source $here/config.ini >/dev/null 2>&1

if [ $# -lt 2 ] ; then
  echo "usage setIPCamExpo.sh day|night camid"
  exit 1
fi

logger  -s -t setIPCamExpo "Setting exposure for $1. Camera is $2, gain is $NIGHTGAIN"
python3 $here/setExpo.py $1 $2 $NIGHTGAIN 
