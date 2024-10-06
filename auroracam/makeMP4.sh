#!/bin/bash
# Copyright (C) Mark McIntyre
#

FPS=60
source ~/vAuroracam/bin/activate

if [ $# -lt 1 ] ; then
    echo usage: ./makeMP4 yyyymmdd_hhmmss {day}
else
    here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
    source $here/config.ini > /dev/null 2>&1

    fldr=$1
    [ $# -gt 1 ] && dayornight=1 || dayornight=0
    export fldr dayornight DATADIR

    touch $DATADIR/../.noreboot
    echo making an mp4 of $DATADIR/$fldr

    python << EOD
import platform, configparser, os, boto3, logging, logging.handlers
from grabImage import makeTimelapse, getAWSKey, setupLogging
hostname = platform.uname().node
thiscfg = configparser.ConfigParser()
local_path =os.path.dirname(os.path.abspath(__file__))
thiscfg.read(os.path.join(local_path, 'config.ini'))
idserver = thiscfg['uploads']['idserver']
sshkey = thiscfg['uploads']['idkey']
setupLogging(thiscfg,'makeMP4_')
awskey, awssec = getAWSKey(idserver,hostname,hostname,sshkey)
conn = boto3.Session(aws_access_key_id=awskey, aws_secret_access_key=awssec)
s3 = conn.resource('s3')
ulloc = thiscfg['uploads']['s3uploadloc']
bucket = ulloc[5:]
camid = thiscfg['auroracam']['camid']
print('${fldr}', camid, bucket, ${dayornight})
makeTimelapse('${DATADIR}/${fldr}', s3, camid, bucket, ${dayornight})
EOD
    rm -f ${DATADIR}/../.noreboot
fi