#!/bin/bash
# Copyright (C) Mark McIntyre
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/config.ini > /dev/null 2>&1
source ~/vAuroracam/bin/activate

cd $DATADIR
python $here/archAndFree.py

cd $DATADIR/../logs
find . -mtime +30 -exec rm -f {} \;
