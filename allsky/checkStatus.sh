#!/bin/bash
#
# script to check and restart allsky if frozen
# Copyright (C) Mark McIntyre
#

srcdir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $srcdir
source ~/vAllsky/bin/activate

python $srcdir/checkAllsky.py
