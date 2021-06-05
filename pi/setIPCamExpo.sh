#!/bin/bash
export PATH=$PATH:/usr/local/bin
# required for SSL with python3
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/openssl/lib:/usr/local/openssl/lib

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source ~/vRMS/bin/activate
source $here/config.ini
cd ~/source/RMS
if [ "$1" == "" ] ; then
  echo "usage setIPCamExpo.sh DAY|NIGHT|REBOOT"
  exit 1
fi
IPCAMADDR=$(grep device .config  |awk -F "rtsp://" '{ print $2 }' | awk -F: '{print $1 }' | uniq)
LOGF=/home/pi/RMS_data/logs/setExpo-`date +%Y%m%d`.log

if [ "$1" == "REBOOT" ] ; then
    DON=`$here/sunwait poll angle -5 51.88N 1.31W`
    logger "Setting exposure for $DON. Camera is $IPCAMADDR"
    python3 $here/SetExpo.py $IPCAMADDR $DON $NIGHTGAIN > $LOGF 2>&1
else
  logger "Setting exposure for $1. Camera is $IPCAMADDR, gain is $NIGHTGAIN" 
  python3 $here/SetExpo.py $IPCAMADDR $1 $NIGHTGAIN > $LOGF 2>&1

  # if running at dusk, add tomorrow's AT jobs
  hr=`date +%H`
  if [ $hr -gt 12 ] ; then
      tms=`$here/sunwait list angle -5 51.88N 1.31W`
      dawn=`echo $tms | cut -d, -f1`
      dusk=`echo $tms | cut -d, -f2`
      echo "$here/setIPCamExpo.sh DAY" | at $dawn tomorrow -M 
      echo "$here/setIPCamExpo.sh NIGHT" | at $dusk tomorrow -M 
  fi
fi