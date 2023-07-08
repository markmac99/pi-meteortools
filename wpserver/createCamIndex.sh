#!/bin/bash
#
# Script to make index file for camera uploads
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/config.ini
mkdir -p $here/logs
cd $DATADIR

idxfile=$TMPDIR/cameraindex.js
currmth=$(date +%Y%m)

echo "\$(function() {" > $idxfile
echo "var table = document.createElement(\"table\");" >> $idxfile
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $idxfile
echo "var header = table.createTHead(); " >> $idxfile
echo "header.className = \"h4\"; " >> $idxfile

camlist=$(ls -1d UK* allsky/startrails allsky/videos)
for cam in $camlist ; do 
    mkdir -p $cam/$currmth 
    aws s3 sync s3://mjmm-data/$cam/ ./$cam --exclude "*" --include "*.js" --include "*.html"
done

camlist=$(ls -1d UK* allsky)
mthlist=$(ls -1dr UK0006/202* | awk -F/ '{print $2}')
if [[ $mthlist != *"$currmth"* ]] ; then mthlist=$(echo $currmth $mthlist ) ; fi
mthlist=$(echo stacks trackstacks $mthlist)

for mth in $mthlist ; do 
    echo "var row = table.insertRow(-1);" >> $idxfile
    for cam in $camlist; do
        echo "var cell = row.insertCell(-1);" >> $idxfile
        if [ "$cam" == "allsky" ] ; then
            if compgen -G "$cam/videos/$mth" > /dev/null ; then 
                echo "cell.innerHTML = \"\\<a href=\\\"/data/mjmm-data/$cam/videos/$mth\\\"\\>$mth\\</a\\>\";" >> $idxfile
            else
                if [ "$mth" == "trackstacks" ] ; then
                    echo "cell.innerHTML = \"\\<a href=\\\"/data/mjmm-data/$cam/startrails\\\"\\>startrails\\</a\\>\";" >> $idxfile
                else
                    echo "cell.innerHTML = \"\";" >> $idxfile
                fi 
            fi
        else
            if compgen -G "$cam/$mth" > /dev/null ; then 
                echo "cell.innerHTML = \"\\<a href=\\\"/data/mjmm-data/$cam/$mth\\\"\\>$mth\\</a\\>\";" >> $idxfile
            else
                echo "cell.innerHTML = \"\";" >> $idxfile
            fi
        fi
    done
done
echo "var row = header.insertRow(0);"  >> $idxfile
i=0
for cam in $camlist; do
    echo "var cell = row.insertCell($i);" >> $idxfile
    if [ "$cam" == "UK9999" ] ; then 
        echo "cell.innerHTML = \"AuroraCam\";" >> $idxfile
    else 
        echo "cell.innerHTML = \"$cam\";" >> $idxfile
    fi
    echo "cell.className = \"small\";" >> $idxfile
    i=$((i+1))
done

echo "var outer_div = document.getElementById(\"cam-list\");"   >> $idxfile
echo "outer_div.appendChild(table);"  >> $idxfile
echo "})"  >> $idxfile

diff $idxfile $DATADIR/cameraindex.js > /dev/null 
if [ $? -gt 0 ] ; then
    echo deploying changes to $DATADIR
    cp $idxfile $DATADIR/cameraindex.js
else
    echo nothing changed
fi

idxfile=$TMPDIR/cameraindex.js
echo "\$(function() {" > $idxfile
echo "var table = document.createElement(\"table\");" >> $idxfile
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $idxfile
echo "var header = table.createTHead(); " >> $idxfile
echo "header.className = \"h4\"; " >> $idxfile

mthlist=$(ls -1dr allsky/startrails/202* | awk -F/ '{print $3}')
if [[ $mthlist != *"$currmth"* ]] ; then mthlist=$(echo $currmth $mthlist ) ; fi

echo "var row = table.insertRow(-1);" >> $idxfile
i=0
for mth in $mthlist ; do 
    if [ $i -eq 5 ] ; then
        echo "var row = table.insertRow(-1);" >> $idxfile
        i=0
    fi
    echo "var cell = row.insertCell(-1);" >> $idxfile
    if compgen -G "allsky/startrails/$mth" > /dev/null ; then 
        echo "cell.innerHTML = \"\\<a href=\\\"/data/mjmm-data/allsky/startrails/$mth\\\"\\>$mth\\</a\\>\";" >> $idxfile
    fi
    i=$((i+1))
done

echo "var outer_div = document.getElementById(\"mthindex\");"   >> $idxfile
echo "outer_div.appendChild(table);"  >> $idxfile
echo "})"  >> $idxfile

diff $idxfile $DATADIR/allsky/startrails/cameraindex.js > /dev/null 
if [ $? -gt 0 ] ; then
    echo deploying startrails changes
    cp $idxfile $DATADIR/allsky/startrails/cameraindex.js
else
    echo nothing changed
fi

camlist=$(ls -1d UK* allsky/startrails allsky/videos)
for cam in $camlist ; do 
    aws s3 sync ./$cam s3://mjmm-data/$cam/  --exclude "*" --include "*.js" --include "*.html"
done

delaymins=120

source ~/tools/vwebstuff/bin/activate
#pip install --upgrade python-crontab ephem

python - << EOD
from crontab import CronTab
import ephem
import datetime

obs = ephem.Observer()
obs.lat = 51.88 / 57.3 
obs.lon = -1.31 / 57.3
obs.elev = 80
obs.horizon = -6.0 / 57.3 # degrees below horizon for darkness

sun = ephem.Sun()
rise = obs.next_rising(sun).datetime()
rise = rise + + datetime.timedelta(minutes=${delaymins})
cron = CronTab(user=True)
found = False
iter=cron.find_command('createCamIndex')
for i in iter:
    if i.is_enabled():
        i.hour.on(rise.hour)
        i.minute.on(rise.minute)
        found = True
if found is False:
    job = cron.new('${here}/createCamIndex.sh > ${here}/logs/createCamIndex.log 2>&1')
    job.hour.on(rise.hour)
    job.minute.on(rise.minute)
cron.write()
EOD

