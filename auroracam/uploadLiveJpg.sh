#!/bin/bash
# Copyright (C) Mark McIntyre
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

hn=$(hostname)
logger -s -t $hn "starting live jpg upload"
source $here/config.ini > /dev/null 2>&1
export DATADIR LOGDIR IPADDRESS NIGHTGAIN
export LAT LON ALT UPLOADLOC CAMID

source ~/vAuroracam/bin/activate
#export PYTHONPATH=~/source/RMS

python $here/grabImage.py $IPADDRESS $hn
