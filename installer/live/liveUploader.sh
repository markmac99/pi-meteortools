#!/bin/bash
source ~/ukmon/.livecreds
source ~/vRMS/bin/activate

mkdir -p ~/ukmon/tmp > /dev/null 2>&1
\rm -f ~/ukmon/tmp/*

curdir=`dirname $1`
ff=`basename $1`
cp $curdir/$ff ~/ukmon/tmp

pushd ~/source/RMS
python -m Utils.BatchFFtoImage ~/ukmon/tmp jpg
popd
pushd ~/ukmon/tmp
# get date and time stamps here
dn=`ls -1tr *.jpg | tail -1`
cam=`echo $dn | cut -d "_" -f2`
dt=`echo $dn | cut -d "_" -f3`
tm=`echo $dn | cut -d "_" -f4`
echo $cam $dt $tm
yr=`echo $dt | cut -c1-4`
mo=`echo $dt | cut -c5-6`
dy=`echo $dt | cut -c7-8`
hr=`echo $tm | cut -c1-2`
mi=`echo $tm | cut -c3-4`
se=`echo $tm | cut -c5-6`

newf=M${dt}_${tm}_${loc}_${cam}
mv $dn ${newf}P.jpg
cat ~/ukmon/template.xml | sed "s/YEAR/${yr}/;s/MONTH/$mo/;s/DAY/$dy/;s/HOUR/$hr/;s/MINUTE/$mi/;s/SEC/$se/;s/LID/$loc/;s/SID/$cam/g" > ~/ukmon/tmp/${newf}.xml

aws s3 cp ${newf}P.jpg s3://ukmon-live/
aws s3 cp ${newf}.xml s3://ukmon-live/

