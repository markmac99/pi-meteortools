#!/bin/bash
#
# Script to make index file for camera uploads
#

htmlfile=index.html
idxfile=cameraindex.js
currmth=$(date +%Y%m)
if [ "$2" != "" ] ; then 
    currmth=$2
fi

cd $HOME/data/mjmm-data/$1/$currmth

echo "<html><head><title>Index of $currmth</title>" > $htmlfile
echo "<link href=\"/data/mjmm-data/css/bootstrap.min.css\" rel=\"stylesheet\">" >> $htmlfile
echo "<link href=\"/data/mjmm-data/css/plugins/metisMenu/metisMenu.min.css\" rel="stylesheet">" >> $htmlfile
echo "<link href=\"/data/mjmm-data/css/plugins/timeline.css\" rel="stylesheet">" >> $htmlfile
echo "<link href=\"/data/mjmm-data/css/plugins/morris.css\" rel="stylesheet">" >> $htmlfile
echo "<link href=\"/data/mjmm-data/css/magnific-popup.css\" rel="stylesheet">" >> $htmlfile
echo "<style>h2{margin-left: 80px;}</style>" >> $htmlfile
echo "<style>p{margin-left: 80px;}</style>" >> $htmlfile
echo "<style>div{margin-left: 80px;margin-right: 80px;}</style>" >> $htmlfile

echo "<link href=\"/data/mjmm-data/css/dragontail.css\" rel=\"stylesheet\">" >> $htmlfile

echo "</head><body>" >> $htmlfile 
echo "<script src=\"/js/jquery.js\"></script>" >> $htmlfile
echo "<script src=\"/js/bootstrap.min.js\"></script>" >> $htmlfile
echo "<script src=\"/js/plugins/morris/raphael.min.js\"></script>" >> $htmlfile
echo "<script src=\"/js/plugins/morris/morris.min.js\"></script>" >> $htmlfile
echo "<script src=\"./$idxfile\"></script>" >> $htmlfile
echo "<h2>List of videos available for this month</h2>" >> $htmlfile
echo "<p><a href=\"https://markmcintyreastro.co.uk/cameradata/\">Back to index</a></p><hr>" >> $htmlfile
echo "<div id=\"mthindex\"></div>" >> $htmlfile
echo "</body></html>"  >> $htmlfile

echo "\$(function() {" > $idxfile
echo "var table = document.createElement(\"table\");" >> $idxfile
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $idxfile
echo "var header = table.createTHead(); " >> $idxfile
echo "header.className = \"h4\"; " >> $idxfile

if [ "$currmth" == "stacks" ] ; then
    mp4list=$(ls -1dr *.jpg)
else
    mp4list=$(ls -1dr *.mp4)
fi
i=0
echo "var row = table.insertRow(-1);" >> $idxfile
for fil in $mp4list ; do 
    if [ $i == 3 ] ; then 
        i=0
        echo "var row = table.insertRow(-1);" >> $idxfile
    fi
    echo "var cell = row.insertCell(-1);" >> $idxfile
    echo "cell.innerHTML = \"\\<a href=\\\"/data/mjmm-data/$1/$currmth/$fil\\\"\\>$fil\\</a\\>\";" >> $idxfile
    chmod 644 $fil
    i=$((i+1))
done

echo "var outer_div = document.getElementById(\"mthindex\");"   >> $idxfile
echo "outer_div.appendChild(table);"  >> $idxfile
echo "})"  >> $idxfile
