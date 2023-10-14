#!/bin/bash
#
# Script to make index file for camera uploads
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/config.ini
mkdir -p $here/logs
cd $DATADIR

source ~/tools/vwebstuff/bin/activate
python $here/makeLatestIndex.py
