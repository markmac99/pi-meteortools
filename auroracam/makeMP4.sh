#!/bin/bash
# Copyright (C) Mark McIntyre
#

FPS=60

if [ $# -lt 1 ] ; then
    echo usage: ./makeMP4 yyyymmdd_hhmmss {day}
else
    here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
    source $here/config.ini > /dev/null 2>&1

    fldr=$1
    camid=$CAMID
    dayornight=$2

    touch $DATADIR/../.noreboot
    cd ${DATADIR}/${fldr}
    echo making an mp4 of $(pwd)
    [ "$dayornight" == "" ] && mp4name=${camid}_${fldr}.mp4 || mp4name=${camid}_${fldr}_day.mp4
    
    ffmpeg -v quiet -r $FPS -pattern_type glob -i "*.jpg" \
            -vcodec libx264 -pix_fmt yuv420p -crf 25 -movflags faststart -g 15 -vf "hqdn3d=4:3:6:4.5,lutyuv=y=gammaval(0.77)"  \
            $mp4name

    mth=${fldr:0:6}
    aws s3 cp $mp4name s3://mjmm-data/${camid}/${mth}/ 
    rm -f ${DATADIR}/../.noreboot
fi