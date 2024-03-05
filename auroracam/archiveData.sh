#!/bin/bash
# Copyright (C) Mark McIntyre
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/config.ini > /dev/null 2>&1
source ~/vAuroracam/bin/activate

cd $DATADIR
aws s3 cp s3://mjmm-data/auroracam/FILES_TO_UPLOAD.inf ~/RMS_data/auroracam/
python $here/archAndFree.py
aws s3 cp ~/RMS_data/auroracam/FILES_TO_UPLOAD.inf  s3://mjmm-data/auroracam/

cd $DATADIR/../logs
find . -mtime +30 -exec rm -f {} \;
