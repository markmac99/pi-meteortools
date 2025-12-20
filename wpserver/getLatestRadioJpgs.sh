#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/config.ini
if [ ! -f /tmp/getLatestRadioJpgs.running ] ; then 
	echo "1" > /tmp/getLatestRadioJpgs.running
	cd $DATADIR/Radio
	aws s3 sync s3://mjmm-data/Radio/ . --exclude "*" --include "sc*.png"
	aws s3 sync s3://mjmm-data/Radio/ . --exclude "*" --include "*.jpg"
	rm -f /tmp/getLatestRadioJpgs.running
else
	echo "already running"
fi 
