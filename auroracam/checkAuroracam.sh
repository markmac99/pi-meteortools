#!/bin/bash
source ~/source/auroracam/config.ini
filetocheck=$DATADIR/../live.jpg

while true
do
  if [ ! -f $DATADIR/../.noreboot ] ; then 
    x=$(find ${filetocheck} -mmin +5)
    if [ "$x" !=  "" ] ; then
      echo it crashed
      sudo reboot
    else
      echo all ok
    fi
  fi
  sleep 30
done
