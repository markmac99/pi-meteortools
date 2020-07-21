#!/bin/bash
cd ~/RMS_data/ArchivedFiles
cam=`grep stationID ~/source/RMS/.config | awk {'print $2}'`
find . -name "$cam*" -type d -mtime +10 -exec ls -1  \; | grep -v bz2 | while read i ; do grep 000000 $i/*.txt > /dev/null ; if [ $? -eq 0 ] ; then echo found && rm -Rf $i ; fi ; done

ls -1 *.bz2 | while read i ; do  [ ! -d  `basename $i _detected.tar.bz2` ] && rm -f $i  ; done

