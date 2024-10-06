#!/bin/bash
# Copyright (C) Mark McIntyre
#
source ~/source/auroracam/config.ini > /dev/null 2>&1
filetocheck=$DATADIR/../live.jpg
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source ~/vAuroracam/bin/activate

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
                    pushd $here
                    python -c "from setExpo import setCameraNetWorkDets;setCameraNetWorkDets('192.168.1.10','$IPADDRESS')"
                     logger -s -t $(ping -c 1 $IPADDRESS| tail -2 | head -1)
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
