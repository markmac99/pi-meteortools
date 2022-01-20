#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/config.ini

cd $DATADIR/Radio

p=/data/mjmm-data/Radio/

idxfile=rmoblist.js
echo "\$(function() {" > rmoblist.js
echo "var table = document.createElement(\"table\");" >> rmoblist.js
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> rmoblist.js
echo "var header = table.createTHead();" >> rmoblist.js
echo "header.className = \"h4\";" >> rmoblist.js 

ls -1d 20* | sort -n -r | while read i ; do
    k=0
    ls -1 $i/*.jpg | sort -n -r | while read j;  do
        if [ $k -eq 0 ] ; then 
            echo "var row = table.insertRow(-1);" >> rmoblist.js
        fi
        echo "var cell = row.insertCell(-1);" >> rmoblist.js
        echo "cell.innerHTML = \"<a href=$p/$j><img src=$p/$j width=100%></a>\";" >> rmoblist.js
        k=$((k+1))
        if [ $k -eq 4 ] ; then k=0 ; fi
    done
done 
echo "var outer_div = document.getElementById(\"rmoblist\");" >> rmoblist.js
echo "outer_div.appendChild(table);" >> rmoblist.js
echo "})" >> rmoblist.js

