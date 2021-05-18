#!/bin/bash
#
# Script to make index file for camera uploads
#

cd $HOME/data/mjmm-data

idxfile=cameraindex.js
currmth=$(date +%Y%m)


echo "\$(function() {" > cameraindex.js
echo "var table = document.createElement(\"table\");" >> cameraindex.js
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> cameraindex.js
echo "var header = table.createTHead(); " >> cameraindex.js
echo "header.className = \"h4\"; " >> cameraindex.js


camlist=$(ls -1d UK* allsky)
mthlist=$(ls -1dr UK0006/202* | awk -F/ '{print $2}')
for mth in $mthlist ; do 
    echo "var row = table.insertRow(-1);" >> cameraindex.js
    for cam in $camlist; do
        echo "var cell = row.insertCell(-1);" >> cameraindex.js
        if [ "$cam" == "allsky" ] ; then
            if compgen -G "$cam/videos/$mth" > /dev/null ; then 
                echo "cell.innerHTML = \"\\<a href=\\\"/data/mjmm-data/$cam/videos/$mth\\\"\\>$mth\\</a\\>\";" >> cameraindex.js
            else
                echo "cell.innerHTML = \"\";" >> cameraindex.js
            fi
        else
            if compgen -G "$cam/$mth" > /dev/null ; then 
                echo "cell.innerHTML = \"\\<a href=\\\"/data/mjmm-data/$cam/$mth\\\"\\>$mth\\</a\\>\";" >> cameraindex.js
            else
                echo "cell.innerHTML = \"\";" >> cameraindex.js
            fi
        fi
    done
done
echo "var row = header.insertRow(0);"  >> cameraindex.js
i=0
for cam in $camlist; do
    echo "var cell = row.insertCell($i);" >> cameraindex.js
    echo "cell.innerHTML = \"$cam\";" >> cameraindex.js
    echo "cell.className = \"small\";" >> cameraindex.js
    i=$((i+1))
    chmod 644 $cam/$currmth/*.mp4
    if [ "$cam" != "allsky" ] ; then 
        ./createMthIndex.sh $cam
    fi
done

echo "var outer_div = document.getElementById(\"cam-list\");"   >> cameraindex.js
echo "outer_div.appendChild(table);"  >> cameraindex.js
echo "})"  >> cameraindex.js
