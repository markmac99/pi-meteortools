#!/bin/bash
# Copyright (C) Mark McIntyre
#
# clear down anything older than 20 days from ArchivedFiles

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source ~/vRMS/bin/activate
cd $here
statid=$1
python -c "from sendToMQTT import sendMatchdataToMqtt;sendMatchdataToMqtt('$statid');"
