#!/bin/bash

# backup RMS config 

srcdir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cp /home/pi/source/RMS/.config $srcdir/bkp/.config.`date +%Y%m`
cp /home/pi/source/RMS/platepar_cmn2010.cal $srcdir/bkp/platepar_cmn2010.cal.`date +%Y%m`
cp /home/pi/source/RMS/mask.bmp $srcdir/bkp/mask.bmp.`date +%Y%m`

mkdir /tmp/rms_config > /dev/null 2>&1
cp /home/pi/source/RMS/.config /tmp/rms_config
cp /home/pi/source/RMS/platepar_cmn2010.cal /tmp/rms_config
cp /home/pi/source/RMS/mask.bmp /tmp/rms_config

cp -p /home/pi/.ssh/id_rsa* /tmp/rms_config
if [ -f /home/pi/.ssh/authorized_keys ] ; then cp -p /home/pi/.ssh/authorized_keys /tmp/rms_config ; fi

cp /home/pi/source/ukmon-pitools/ukmon.ini /tmp/rms_config
cp -pr /home/pi/.ssh/ukmon* /tmp/rms_config

tarfname=~/RMS_data/RMSconfig-$(date +%Y%m%d).tgz
cd /tmp
tar -cvzf $tarfname ./rms_config

echo "now copy $tarfname to a safe place"