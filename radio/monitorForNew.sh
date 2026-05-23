#!/bin/bash

# shell script to monitor for new detections

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/config.ini

# kill any existing instances of the script
pgrep -f "/bin/bash $0" | egrep -v $$ | while read i ; do kill -9 $i ; done > /dev/null 2>&1

cd $LOGDIR
mkdir -p done

logfile=$(ls -1tr meteor_radar*.log | tail -1)
donelist=$LOGDIR/uploaded.txt

tail -fn0 $logfile  | while read line ; do 
    if [[ "$line" =~ "Saving /home" ]] ; then  
        sleep 10
        datafile=${line:7:100}
        basedatafile=$(basename $datafile)
        grep $basedatafile $donelist > /dev/null
        if [ $? == 1 ] ; then 
            /usr/local/bin/aws s3 cp $datafile "s3://mjmm-rawradiodata/tmp/$basedatafile"
            echo $basedatafile >> $donelist
            cat $donelist | tail -10 > /tmp/uploaded.txt
            mv -f /tmp/uploaded.txt $donelist
        fi 
    fi 
done

