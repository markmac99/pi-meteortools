#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
cd $HOME/RMS_data/logs
grep rabbing $(ls -1 log*.log* | tail -1) | awk -F" " '{print $2}' |awk -F"-" '{print $1}' > /home/pi/RMS_data/logs/grabbing-`date +%Y%m%d`.log
