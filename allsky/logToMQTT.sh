#!/bin/bash
# Copyright (C) Mark McIntyre
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source ~/vAllsky/bin/activate

dt=$(date '+%d/%m/%Y %H:%M:%S')
tm=$(vcgencmd measure_temp | cut -d= -f2)
ds=$(df -h . | tail -1 | awk -F" " '{print $5 }')

#grep BROKER $here/config.ini
if [ $? -eq 1 ] ; then 
    echo $dt $tm  >> /home/pi/RMS_data/logs/temperature-`date +%Y%m%d`.log
else
    cd $here
    python -c "from sendToMQTT import sendOtherData ; sendOtherData(\"${tm}\",\"${ds}\") ; "
fi 
