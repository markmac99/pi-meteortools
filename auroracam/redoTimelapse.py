from grabImage import makeTimelapse, getAWSKey, setupLogging
import platform
import os
import sys
import configparser
import boto3
import logging

log = logging.getLogger("logger")


dirpath = sys.argv[1]
force = False
if len(sys.argv) > 2:
    if int(sys.argv[2])==1:
        force = True

thiscfg = configparser.ConfigParser()
local_path =os.path.dirname(os.path.abspath(__file__))
thiscfg.read(os.path.join(local_path, 'config.ini'))
ulloc = thiscfg['auroracam']['uploadloc']
camid = thiscfg['auroracam']['camid']
datadir = os.path.expanduser(thiscfg['auroracam']['datadir'])
hostname = platform.uname().node

setupLogging(thiscfg)
if ulloc[:5] == 's3://':
    idserver = thiscfg['auroracam']['idserver']
    sshkey = thiscfg['auroracam']['idfile']
    awskey, awssec = getAWSKey(idserver, hostname, hostname, sshkey)
    if not awskey:
        log.error('unable to find AWS key')
        exit(1)
    conn = boto3.Session(aws_access_key_id=awskey, aws_secret_access_key=awssec)
    s3 = conn.resource('s3')
    bucket = ulloc[5:]
else:
    print('not uploading to AWS S3')
    s3 = None
    bucket = None
dirname = os.path.join(datadir, dirpath)
                          
makeTimelapse(dirname, s3, camid, bucket, daytimelapse=False, maketimelapse=force)
