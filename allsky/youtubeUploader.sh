#!/bin/bash

# Copyright (C) Mark McIntyre
#
# install the cronjobs

srcdir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $srcdir
source ~/vAllsky/bin/activate

python $srcdir/ytUpload.py /var/log/allsky.log $HOME/src/allsky