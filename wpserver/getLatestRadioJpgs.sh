#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/config.ini

cd $DATADIR/Radio
aws s3 sync s3://mjmm-data/Radio/ . --exclude "*" --include "*latest.jpg" --include "screenshot*.jpg"

cd $DATADIR/
camlist=$(ls -1d UK* allsky/startrails allsky/videos)
for cam in $camlist ; do 
    mkdir -p $cam/$currmth 
    aws s3 sync s3://mjmm-data/$cam/ ./$cam --exclude "*" --include "*.js" --include "*.html"
done
