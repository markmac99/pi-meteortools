#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/config.ini

cd $DATADIR

# find folders older than 7 days and archive them to a gzipped tarball
find . -type d -mtime +7 | while read i 
do
    bn=$(basename $i)
    tar cvfz ./$bn.tgz ./$bn/*.*
    if [ $? -eq 0 ] ; then 
        rm -Rf ./$bn
    else
        echo archiving failed
    fi 
done

# delete archives after a further seven days
# note that the archive will have the datestamp from when it was created
find . -type f -name "2*.tgz" -mtime +7 | while read i 
do
    rm -f $i
done 

# purge older logfiles
cd $LOGDIR
find . -type f -mtime +21 -name "*.gz" | while read i 
do
    rm -f $i
done
find . -type f -mtime +7 -name "*.log" | while read i 
do
    gzip $i 
done
