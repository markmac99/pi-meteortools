#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

hn=$(hostname)
logger -s -t $hn "starting live jpg upload"
source $here/config.ini
export DATADIR LOGDIR IPADDRESS NIGHTGAIN

source ~/venvs/vRMS/bin/activate
export PYTHONPATH=~/source/RMS

python $here/grabImage.py $IPADDRESS $hn