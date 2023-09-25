#!/bin/bash
# Copyright (C) Mark McIntyre
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/config.ini > /dev/null 2>&1

cd $DATADIR

DAYS=4
# find older folders and archive them to a tarball
echo "checking for folders older than $DAYS days to compress"
find . -type d -mtime +${DAYS} | while read i 
do
    bn=$(basename $i)
    if compgen -G ./$bn/*.* > /dev/null ; then 
        echo "compressing then removing $bn as more than ${DAYS} days old"
        tar cvfz ./$bn.tgz ./$bn/*.*
        if [ $? -eq 0 ] ; then 
            rm -Rf ./$bn
        else
            echo archiving failed
        fi
    else
        echo "removing empty $bn"
        rm -Rf ./$bn
    fi
done

# delete archives after a further period
# note that the archive will have the datestamp from when it was created
echo "looking for tarballs older than ${DAYS} days to delete"
find . -type f -name "2*.tgz" -mtime +${DAYS} | while read i 
do
    echo "removing $i as more than ${DAYS} days old"
    rm -f $i
done 

# purge older logfiles
echo "looking for older logfiles to delete or compress"
cd $LOGDIR
find . -type f -mtime +21 -name "*.gz" | while read i 
do
    echo "removing $i as more than 21 days old"
    rm -f $i
done
find . -type f -mtime +${DAYS} -name "*.log" | while read i 
do
    echo "compressing $i as more than ${DAYS} days old"
    gzip $i 
done
