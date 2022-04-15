#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/config.ini

source ~/venvs/wmpl/bin/activate
cd $here
ym=$(date +%Y%m)
python $here/lambdaForRadio.py ~/data/rawradiodata/ ~/data/Radio/ ${ym}
