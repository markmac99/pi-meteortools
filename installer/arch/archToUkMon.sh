#!/bin/bash
source ~/ukmon/.archcreds
dn=`ls -1tr ~/RMS_data/ArchivedFiles/ | grep -v bz2 | tail -1`
cam=`echo $dn | cut -d _ -f1`
dt=`echo $dn | cut -d _ -f2`
yr=`echo $dt | cut -c1-4`
ym=`echo $dt | cut -c1-6`
pth=$loc/$cam/$yr/$ym/$dt/
ftpd=`wc -l ~/RMS_data/ArchivedFiles/$dn/*.csv | tail -1 | awk '{print $1}'`
if [[ $ftpd -gt 1 ]] ; then 
  aws s3 sync ~/RMS_data/ArchivedFiles/$dn s3://ukmon-shared/archive/$pth --exclude "*" --include "*.png" --include "*.json" --include "*.cal" --include "*.csv" --include "*.jpg" --include "*.txt" --include "*.mp4"
else
  echo nothing to do today
fi
