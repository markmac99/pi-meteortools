#!/bin/bash

# Copyright (C) Mark McIntyre
#
# install the cronjobs

source ~/.bashrc
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $here
conda activate openhabstuff
pip install -r requirements.txt

python -c "from sendToMQTT import addCrontabs;addCrontabs();"
