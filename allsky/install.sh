#!/bin/bash

# Copyright (C) Mark McIntyre
#
# install the cronjobs

srcdir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $srcdir
source ~/vRMS/bin/activate
pip install -r requirements.txt
python -c "from sendToMQTT import addCrontabs;addCrontabs();"
