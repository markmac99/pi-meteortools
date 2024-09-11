#!/bin/bash
# Copyright (C) Mark McIntyre
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

hn=$(hostname)
logger -s -t $hn "starting auroracam"
source $here/config.ini > /dev/null 2>&1
export DATADIR LOGDIR IPADDRESS NIGHTGAIN
export LAT LON ALT UPLOADLOC CAMID

source ~/vAuroracam/bin/activate

pids=$(ps -ef | grep ${here}/grabImage | egrep -v "grep|$$" | awk '{print $2}')
[ "$pids" != "" ] && kill -9 $pids

python $here/auroraCam.py $IPADDRESS 
