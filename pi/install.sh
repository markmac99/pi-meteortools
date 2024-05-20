#!/bin/bash

# Copyright (C) Mark McIntyre
#
# install the cronjobs

srcdir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $srcdir
sudo apt-get install libgeos-dev
pip install -r requirements.txt
python -c "from dailyPostProc import addCrontabs;addCrontabs();"
