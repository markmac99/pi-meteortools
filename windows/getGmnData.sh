#!/bin/bash

cd /mnt/f/videos/meteorcam/gmndata

wget -N https://globalmeteornetwork.org/data/traj_summary_data/monthly/

cat index.html | 	while read i 
do
	fn=$(echo $i | awk -F ">" '{print $2}')
	if [ "${fn:0:4}" == "traj" ]
	then
		fnam=${fn:0:-3}
		wget -N https://globalmeteornetwork.org/data/traj_summary_data/monthly/$fnam
	fi
done
