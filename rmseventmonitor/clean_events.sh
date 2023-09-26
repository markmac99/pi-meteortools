#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source ~/anaconda3/etc/profile.d/conda.sh

conda activate ukmon-shared

python cleanup.py $1
