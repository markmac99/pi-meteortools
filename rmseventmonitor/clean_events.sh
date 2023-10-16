#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

if [ -f ~/miniconda3/etc/profile.d/conda.sh ] ; then 
    source ~/miniconda3/etc/profile.d/conda.sh
else
    source ~/anaconda3/etc/profile.d/conda.sh
fi 

conda activate ukmon-shared

python cleanup.py $1
