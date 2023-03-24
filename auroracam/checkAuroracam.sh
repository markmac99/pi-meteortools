#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
source ~/source/auroracam/config.ini
filetocheck=$DATADIR/../live.jpg

while true
do
    if [ ! -f $DATADIR/../.noreboot ] ; then 
        x=$(find ${filetocheck} -mmin +5)
        if [ "$x" !=  "" ] ; then
            logger -s -t checkAuroracam "file late: checking camera address is right"
            ping -c 1  -w 1 $IPADDRESS > /dev/null 2>&1
            if [ $? -eq 1 ] ; then 
                logger -s -t checkAuroracam "no response, looking on default address"
                ping -c 1  -w 1 192.168.1.10 > /dev/null 2>&1
                if [ $? -eq 0 ] ; then 
                    logger -s -t checkAuroracam "trying to force address change"
                    source ~/venvs/vRMS/bin/activate
                    cd ~/source/RMS 
                    timeout 5 python -m Utils.SetCameraAddress 192.168.1.10 $IPADDRESS
                    logger -s -t checkAuroracam "address changed"
                else
                    logger -s -t checkAuroracam "camera seems dead"
                fi
            else
                logger -s -t checkAuroracam "camera ok, likely software failure, rebooting"
                sudo reboot
            fi
        fi
    fi
    sleep 30
done
