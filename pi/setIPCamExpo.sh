#!/bin/bash
# Copyright (C) Mark McIntyre
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $HOME/vRMS/bin/activate
source $here/config.ini >/dev/null 2>&1

if [ $# -lt 2 ] ; then
  echo "usage setIPCamExpo.sh day|night"
  exit 1
fi

logger  -s -t setIPCamExpo "Setting exposure for $1
python3 $here/setExpo.py $1
