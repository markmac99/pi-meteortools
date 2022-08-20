#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

hn=$(hostname)
logger -s -t $hn "starting live jpg upload"

statid=$(grep stationID ~/source/RMS/.config | awk '{print $2}')
while [ "$statid" == "XX0001" ] ; do
    echo statid is $statid, sleeping for 20s
    sleep 20
    statid=$(grep stationID ~/source/RMS/.config | awk '{print $2}')
done
ip=$(grep device ~/source/RMS/.config  |awk -F "rtsp://" '{ print $2 }' | awk -F: '{print $1 }' | uniq)

if [ "$hn" == "testpi4" ] ; then 
    targ=auroracam
else
    targ=$hn
fi 
source ~/vRMS/bin/activate
python $here/grabImage.py $ip ~/RMS_data $targ
