#!/bin/bash
srcdir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $srcdir
source ~/vAllsky/bin/activate

tod=$(date +%Y-%m-%d)

egrep "Timelapse complete" /var/log/allsky.log | grep $tod

if [ $? -eq 1 ] 
then
    echo timelapse incomplete
    prevday=$(date --date=yesterday +%Y%m%d)
    ~/src/allsky/scripts/generateForDay.sh  --timelapse $prevday
    ~/src/allsky/scripts/generateForDay.sh  --upload --timelapse $prevday
fi 