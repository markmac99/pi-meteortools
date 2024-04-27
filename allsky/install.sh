#!/bin/bash

# Copyright (C) Mark McIntyre
#
# install the cronjobs

srcdir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $srcdir
pip install -r requirements.txt

python -c "from semdToMQTT import addCrontabs;addCrontabs();"
