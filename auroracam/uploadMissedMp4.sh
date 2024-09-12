#!/bin/bash
# Copyright (C) Mark McIntyre
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source ~/vAuroracam/bin/activate

python $here/redoTimelapse.py $1
