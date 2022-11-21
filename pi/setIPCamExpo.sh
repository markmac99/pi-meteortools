#!/bin/bash
export PATH=$PATH:/usr/local/bin
# required for SSL with python3
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/openssl/lib:/usr/local/openssl/lib

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source ~/vRMS/bin/activate
source $here/config.ini >/dev/null 2>&1

cd $RMSDIR
if [ "$1" == "" ] ; then
  echo "usage setIPCamExpo.sh DAY|NIGHT"
  exit 1
fi
IPCAMADDR=$(grep device .config  |awk -F "rtsp://" '{ print $2 }' | awk -F: '{print $1 }' | uniq)

logger  -s -t setIPCamExpo "Setting exposure for $1. Camera is $IPCAMADDR, gain is $NIGHTGAIN"
python3 $here/SetExpo.py $IPCAMADDR $1 $NIGHTGAIN
