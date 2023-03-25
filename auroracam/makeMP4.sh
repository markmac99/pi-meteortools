#!/bin/bash
# Copyright (C) Mark McIntyre
#
if [ $# -lt 1 ] ; then
    echo usage: ./makeMP4 yyyymmdd_hhmmss
else
    here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
    source $here/config.ini

    fldr=$1
    camid=$CAMID

    touch $DATADIR/../.noreboot
    cd ${DATADIR}/${fldr}
    echo making an mp4 of $(pwd)
    ffmpeg -v quiet -r 60 -pattern_type glob -i "*.jpg" \
            -vcodec libx264 -pix_fmt yuv420p -crf 25 -movflags faststart -g 15 -vf "hqdn3d=4:3:6:4.5,lutyuv=y=gammaval(0.77)"  \
            ${camid}_${fldr}.mp4

    mth=${fldr:0:6}
    aws s3 cp ${camid}_${fldr}.mp4 s3://mjmm-data/${camid}/${mth}/ 
    rm -f ${DATADIR}/../.noreboot
fi