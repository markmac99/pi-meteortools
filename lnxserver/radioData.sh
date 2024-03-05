#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $HOME/miniconda3/bin/activate meteorcam

source $here/config.ini
python $here/getRadioData.py
