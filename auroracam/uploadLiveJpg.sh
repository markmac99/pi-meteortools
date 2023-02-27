#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

hn=$(hostname)
logger -s -t $hn "starting live jpg upload"
source $here/config.ini
export DATADIR LOGDIR IPADDRESS NIGHTGAIN
export LAT LON ALT UPLOADLOC

source ~/vAuroracam/bin/activate
#export PYTHONPATH=~/source/RMS

python $here/grabImage.py $IPADDRESS $hn
