#!/bin/bash

# Copyright (C) Mark McIntyre
#
# install the cronjobs

srcdir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $srcdir
source ~/vAllsky/bin/activate
pip install -r requirements.txt
python -c "from sendToMQTT import addCrontabs;addCrontabs();"

appname=checkallsky

sudo cp $srcdir/$appname.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $appname
sudo systemctl restart $appname
