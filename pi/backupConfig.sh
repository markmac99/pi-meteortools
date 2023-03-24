#!/bin/bash

# Copyright (C) Mark McIntyre
#
# backup RMS config 

srcdir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cp $HOME/source/RMS/.config $srcdir/bkp/.config.`date +%Y%m`
cp $HOME/source/RMS/platepar_cmn2010.cal $srcdir/bkp/platepar_cmn2010.cal.`date +%Y%m`
cp $HOME/source/RMS/mask.bmp $srcdir/bkp/mask.bmp.`date +%Y%m`

mkdir /tmp/rms_config > /dev/null 2>&1
cp $HOME/source/RMS/.config /tmp/rms_config
cp $HOME/source/RMS/platepar_cmn2010.cal /tmp/rms_config
cp $HOME/source/RMS/mask.bmp /tmp/rms_config

cp -p $HOME/.ssh/id_rsa* /tmp/rms_config
if [ -f $HOME/.ssh/authorized_keys ] ; then cp -p $HOME/.ssh/authorized_keys /tmp/rms_config ; fi

cp $HOME/source/ukmon-pitools/ukmon.ini /tmp/rms_config
cp -pr $HOME/.ssh/ukmon* /tmp/rms_config

tarfname=$HOME/RMS_data/RMSconfig-$(date +%Y%m%d).tgz
cd /tmp
tar -cvzf $tarfname ./rms_config

echo "now copy $tarfname to a safe place"