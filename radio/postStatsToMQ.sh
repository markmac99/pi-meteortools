#!/bin/bash

# copyright Mark McIntyre, 2025-
# publish stats to MQ

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/config.ini
source ~/source/tackley-tools/config.ini > /dev/null 2>&1

currdt=$(date +%Y-%m-%d,)
currhr=$(date +%Y-%m-%d,%H)
lastcsv=$(ls -1 $LOGDIR/20*.csv | tail -1)
dailyct=$(egrep "$currdt" $lastcsv | wc -l)
hourlyct=$(egrep "$currhr" $lastcsv | wc -l)
now=$(date +%Y-%m-%dT%H:%M:%SZ)
/usr/bin/mosquitto_pub -h $BROKER -u $USERNAME -P $PASSWORD -t meteorcams/radiopi/hourly -m $hourlyct
/usr/bin/mosquitto_pub -h $BROKER -u $USERNAME -P $PASSWORD -t meteorcams/radiopi/daily -m $dailyct
# last update must be persistent so that the monitor doesnt stall
/usr/bin/mosquitto_pub -h $BROKER -u $USERNAME -P $PASSWORD -t meteorcams/radiopi/lastupdate -r -m $now