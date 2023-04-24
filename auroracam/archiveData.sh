#!/bin/bash
# Copyright (C) Mark McIntyre
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/config.ini > /dev/null 2>&1

cd $DATADIR

# find folders older than 7 days and archive them to a tarball
echo "checking for folders older than 7 days to compress"
find . -type d -mtime +7 | while read i 
do
    bn=$(basename $i)
    if compgen -G ./$bn/*.* > /dev/null ; then 
        echo "compressing then removing $bn as more than 7 days old"
        tar cvf ./$bn.tar ./$bn/*.*
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

# delete archives after a further seven days
# note that the archive will have the datestamp from when it was created
echo "looking for tarballs older than 7 days to delete"
find . -type f -name "2*.tar" -mtime +7 | while read i 
do
    echo "removing $i as more than 7 days old"
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
find . -type f -mtime +7 -name "*.log" | while read i 
do
    echo "compressing $i as more than 7 days old"
    gzip $i 
done
