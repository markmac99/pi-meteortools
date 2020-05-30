#!/bin/bash
dt=`date '+%d/%m/%Y %H:%M:%S'`
tm=`vcgencmd measure_temp | cut -d= -f2`
echo $dt $tm  >> /home/pi/RMS_data/logs/temperature.log