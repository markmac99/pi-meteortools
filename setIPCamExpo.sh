#!/bin/bash

source ~/vRMS/bin/activate
cd ~/source/RMS
if [ "$1" == "" ] ; then
  echo "usage setIPCamExpo.sh DAY|NIGHT"
  exit 1
fi
IPCAMADDR=` grep device .config | grep -v '#' | awk '{print $6}' | cut -d '/' -f3 | cut -d: -f1`
python3 /home/pi/mjmm/SetExpo.py $IPCAMADDR $1

# if running at dusk, add tomorrow's AT jobs
hr=`date +%H`
if [ $hr -gt 12 ] ; then
    tms=`/home/pi/mjmm/sunwait list 51.88N 1.31W`
    dawn=`echo $tms | cut -d, -f1`
    dusk=`echo $tms | cut -d, -f2`
    echo "/home/pi/mjmm/setIPCamExpo.sh DAY" | at $dawn tomorrow
    echo "/home/pi/mjmm/setIPCamExpo.sh NIGHT" | at $dusk tomorrow
fi