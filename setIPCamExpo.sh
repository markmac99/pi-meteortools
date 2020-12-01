#!/bin/bash
export PATH=$PATH:/usr/local/bin
# required for SSL with python3
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/openssl/lib:/usr/local/openssl/lib

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source ~/vRMS/bin/activate
cd ~/source/RMS
if [ "$1" == "" ] ; then
  echo "usage setIPCamExpo.sh DAY|NIGHT|REBOOT"
  exit 1
fi
PAR3=`grep device .config | grep -v '#' | awk '{print $3}'`
if [ "$PAR3" == "protocols=tcp" ] ; then 
  IPCAMADDR=` grep device .config | grep -v '#' | awk '{print $6}' | cut -d '/' -f3 | cut -d: -f1`
else
  IPCAMADDR=` grep device .config | grep -v '#' | awk '{print $3}' | cut -d '/' -f3 | cut -d: -f1`
fi 
LOGF=/home/pi/RMS_data/logs/setExpo-`date +%Y%m%d`.log

if [ "$1" == "REBOOT" ] ; then
    DON=`$here/sunwait poll 51.88N 1.31W`
    logger "Setting exposure for $DON. Camera is $IPCAMADDR"
    python3 $here/SetExpo.py $IPCAMADDR $DON > $LOGF 2>&1
else
  logger "Setting exposure for $1. Camera is $IPCAMADDR" 
  python3 $here/SetExpo.py $IPCAMADDR $1 > $LOGF 2>&1

  # if running at dusk, add tomorrow's AT jobs
  hr=`date +%H`
  if [ $hr -gt 12 ] ; then
      tms=`$here/sunwait list 51.88N 1.31W`
      dawn=`echo $tms | cut -d, -f1`
      dusk=`echo $tms | cut -d, -f2`
      echo "$here/setIPCamExpo.sh DAY" | at $dawn tomorrow
      echo "$here/setIPCamExpo.sh NIGHT" | at $dusk tomorrow
  fi
fi