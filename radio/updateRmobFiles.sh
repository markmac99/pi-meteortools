#!/bin/bash

# shell script to update the RMOB-style csv files

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

# interesting data is already being pushed to AWS
cd $HOME/radar_data/Captures
find . -mtime +45 -exec rm -Rf {} \;

# keep two months' of logs as we need at least that for the above processig
cd $HOME/radar_data/Logs
find . -mtime +62 -exec rm -Rf {} \;
