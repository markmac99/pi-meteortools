#!/bin/bash
# Copyright (C) Mark McIntyre
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source ~/vRMS/bin/activate

dt=$(date '+%d/%m/%Y %H:%M:%S')
vcgencmd > /dev/null 2>&1
if [ $? != 0 ] ; then 
    tm=$(cat /sys/class/thermal/thermal_zone0/temp | awk '{ print ($1 / 1000) "°C" }')
else
    tm=$(vcgencmd measure_temp | cut -d= -f2)
fi
if [ $? -eq 1 ] ; then 
    echo $dt $tm  >> /home/pi/RMS_data/logs/temperature-`date +%Y%m%d`.log
else
    cd $here
    statid=$1
    if [ -d ~/source/Stations/${statid} ] ; then
        datadir=$(grep data_dir: $HOME/source/Stations/${statid}/.config | awk '{print $2}')
    else
        datadir=$(grep data_dir: $HOME/source/RMS/.config | awk '{print $2}')
    fi 
    ds=$(python -c "import os;from shutil import disk_usage;x=disk_usage(os.path.expanduser('${datadir}'));print(round(x.used/x.total*100,4));")

    #grep BROKER $here/config.ini
    python -c "from sendToMQTT import sendOtherData;sendOtherData('${tm}','${ds}', statid='$statid') ; "
fi 
