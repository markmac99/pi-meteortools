#!/bin/bash
#
# Script to make index file for camera uploads
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/config.ini
cd $DATADIR

idxfile=$TMPDIR/cameraindex.js
currmth=$(date +%Y%m)

echo "\$(function() {" > $idxfile
echo "var table = document.createElement(\"table\");" >> $idxfile
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $idxfile
echo "var header = table.createTHead(); " >> $idxfile
echo "header.className = \"h4\"; " >> $idxfile


camlist=$(ls -1d UK* allsky)
mthlist=$(ls -1dr UK0006/202* | awk -F/ '{print $2}')
mthlist=$(echo stacks trackstacks $mthlist)
for mth in $mthlist ; do 
    echo "var row = table.insertRow(-1);" >> $idxfile
    for cam in $camlist; do
        echo "var cell = row.insertCell(-1);" >> $idxfile
        if [ "$cam" == "allsky" ] ; then
            if compgen -G "$cam/videos/$mth" > /dev/null ; then 
                echo "cell.innerHTML = \"\\<a href=\\\"/data/mjmm-data/$cam/videos/$mth\\\"\\>$mth\\</a\\>\";" >> $idxfile
            else
                echo "cell.innerHTML = \"\";" >> $idxfile
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
    if [ "$cam" != "allsky" ] ; then 
        $here/createMthIndex.sh $cam
        $here/createMthIndex.sh $cam stacks
        $here/createMthIndex.sh $cam trackstacks
    else
        $here/createAllskyIndex.sh
    fi
done

echo "var outer_div = document.getElementById(\"cam-list\");"   >> $idxfile
echo "outer_div.appendChild(table);"  >> $idxfile
echo "})"  >> $idxfile

diff $idxfile $DATADIR/cameraindex.js > /dev/null 
if [ $? -gt 0 ] ; then
    echo deploying changes
    cp $idxfile $DATADIR/cameraindex.js
else
    echo nothing changed
fi
