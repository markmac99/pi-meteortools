#!/bin/bash

# shell script to monitor for new detections

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/config.ini

cd $LOGDIR
mkdir -p done
# check last two here to allow for changes over monthend
ls -1tr 20*.csv | tail -2 | while read i ; do 
    if [[ -f done/$i ]] ; then
        diff $i done/$i > /dev/null
        if [ $? == 1 ] ; then
            yr=${i:0:4}
            mth=${i:5:2}
            targname="s3://mjmm-rawradiodata/raw/event_log_${yr}${mth}.csv"
            /usr/local/bin/aws s3 cp $i $targname
            cp $i done/
            /usr/local/bin/aws s3 sync . s3://mjmm-data/Radio/${yr}/${yr}${mth}/  --exclude "*" --include "R${yr}${mth}*.csv"
        fi
    else
        yr=${i:0:4}
        mth=${i:5:2}
        targname="s3://mjmm-rawradiodata/raw/event_log_${yr}${mth}.csv"
        /usr/local/bin/aws s3 cp $i $targname
        cp $i done/
        /usr/local/bin/aws s3 sync . s3://mjmm-data/Radio/${yr}/${yr}${mth}/  --exclude "*" --include "R${yr}${mth}*.csv"
    fi 
done 
