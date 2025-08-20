#!/bin/bash
# Copyright (C) Mark McIntyre
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $HOME/vRMS/bin/activate
source $here/config.ini >/dev/null 2>&1
cd $here
statid=$1
if [ "$statid" == "" ] ; then
    python -c "from sendToMQTT import sendStarCountToMqtt; sendStarCountToMqtt();"
else
    python -c "from sendToMQTT import sendStarCountToMqtt; sendStarCountToMqtt(statid='$statid');"
fi
