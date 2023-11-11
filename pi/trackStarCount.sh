#!/bin/bash
# Copyright (C) Mark McIntyre
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $HOME/vRMS/bin/activate
source $here/config.ini >/dev/null 2>&1

cd $RMSDIR
export PYTHONPATH=$here:$PYTHONPATH
logfile=$(ls -1 ~/RMS_data/logs/log*.log* | tail -1)
starcount=$(grep "Detected stars" $logfile | tail -1 | awk '{print $6}')
[ -z $starcount ] && starcount=0
echo $starcount stars visible
python -c "from sendToMQTT import sendStarCountToMqtt; sendStarCountToMqtt($starcount);"
