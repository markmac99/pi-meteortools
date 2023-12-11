#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/config.ini
active=$(ps -ef | grep getLatestRadioJpgs | grep -v grep | awk '{print $2}')
if [ "$active" == "" ] ; then 
	cd $DATADIR/Radio
	#aws s3 sync s3://mjmm-data/Radio/ . --exclude "*" --include "*latest.jpg" --include "screenshot*.jpg"
	aws s3 cp s3://mjmm-data/Radio/RMOB_latest.jpg .
	aws s3 cp s3://mjmm-data/Radio/3months_latest.jpg .
	aws s3 cp s3://mjmm-data/Radio/screenshot1.jpg .
	aws s3 cp s3://mjmm-data/Radio/screenshot2.jpg .

	#cd $DATADIR/
	#camlist=$(ls -1d UK* allsky/startrails allsky/videos)
	#for cam in $camlist ; do 
	#    mkdir -p $cam/$currmth 
	#    aws s3 sync s3://mjmm-data/$cam/ ./$cam --exclude "*" --include "*.js" --include "*.html"
	#done
fi 
