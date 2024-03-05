#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/config.ini
if [ ! -f /tmp/getLatestRadioJpgs.running ] ; then 
	echo "1" > /tmp/getLatestRadioJpgs.running
	cd $DATADIR/Radio
	#aws s3 sync s3://mjmm-data/Radio/ . --exclude "*" --include "*latest.jpg" --include "screenshot*.jpg"
	aws s3 cp s3://mjmm-data/Radio/RMOB_latest.jpg .
	aws s3 cp s3://mjmm-data/Radio/3months_latest.jpg .
	aws s3 cp s3://mjmm-data/Radio/screenshot1.jpg .
	aws s3 cp s3://mjmm-data/Radio/screenshot2.jpg .
	rm -f /tmp/getLatestRadioJpgs.running
else
	echo "already running"
fi 
