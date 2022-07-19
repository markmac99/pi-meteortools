#!/bin/bash
echo $1
hn=$1

cd /mnt/f/videos/MeteorCam/config

mkdir $hn > /dev/null 2>%1

rsync ${hn}:source/RMS/platepar* $hn/
rsync ${hn}:source/RMS/mask* $hn/
rsync ${hn}:source/RMS/.config $hn/
rsync ${hn}:.rmsautorunflag $hn/ > /dev/null 2>&1

#ssh keys and config
rsync -avz ${hn}:.ssh/* $hn/.ssh/

# ukmon settings
rsync ${hn}:source/ukmon-pitools/ukmon.ini $hn
rsync ${hn}:source/ukmon-pitools/.firstrun $hn > /dev/null 2>&1
rsync ${hn}:source/ukmon-pitools/domp4s $hn > /dev/null 2>&1
rsync ${hn}:source/ukmon-pitools/dotimelapse $hn > /dev/null 2>&1
rsync ${hn}:source/ukmon-pitools/extrascript $hn > /dev/null 2>&1

# mjmm settings
scp $hn:mjmm/*.pickle $hn/ > /dev/null 2>&1
