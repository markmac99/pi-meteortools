#!/bin/bash

# backup RMS config 

srcdir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $srcdir/config.ini

cp /home/pi/source/RMS/.config $srcdir/bkp/.config.`date +%Y%m`
cp /home/pi/source/RMS/platepar_cmn2010.cal $srcdir/bkp/platepar_cmn2010.cal.`date +%Y%m`
cp /home/pi/source/RMS/mask.bmp $srcdir/bkp/mask.bmp.`date +%Y%m`
