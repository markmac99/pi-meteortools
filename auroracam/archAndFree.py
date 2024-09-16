# copyright (c) Mark McIntyre, 2024-
#
# Python script to free diskspace on Auroracam
# 
# The script loops through the folders and files in $DATADIR, checking if they're in 
# FILES_TO_UPLOAD.inf. 
# If present, the folder is compressed and uploaded to my server.
# For each folder and file a check is made if there's sufficient free space for the next 
# night's run and folder or file is deleted if necessary. 
# At least three days data are always kept. 

import shutil
import os
import configparser
import datetime
import platform
import paramiko
import logging
import boto3
from auroraCam import getAWSConn, setupLogging

log = logging.getLogger("logger")


def getFilesToUpload(datadir, bucket, awskey, awssec):
    """
    Load the current list of folders/files to be archived 

    Parameters
        datadir [string] datadir to store file in
        bucket  [string] source bucket
        awskey  [string] aws access key
        awssec  [string] aws secret key
        datadir [string] datadir to store file in
        bucket  [string] source bucket
        awskey  [string] aws access key
        awssec  [string] aws secret key
    """
    conn = boto3.Session(aws_access_key_id=awskey, aws_secret_access_key=awssec) 
    s3 = conn.client('s3')
    s3.download_file(bucket, 'auroracam/FILES_TO_UPLOAD.inf', os.path.join(datadir,'FILES_TO_UPLOAD.inf'))
    conn = boto3.Session(aws_access_key_id=awskey, aws_secret_access_key=awssec) 
    s3 = conn.client('s3')
    s3.download_file(bucket, 'auroracam/FILES_TO_UPLOAD.inf', os.path.join(datadir,'FILES_TO_UPLOAD.inf'))
    dirnames = open(os.path.join(datadir, 'FILES_TO_UPLOAD.inf'), 'r').read().splitlines()
    return dirnames


def getListOfNew(datadir, thiscfg):
    log.info('getting list of files to upload')
    archserver = thiscfg['archive']['archserver']
    if archserver == '':
        # not archiving files, so do nothing
        return []
    tod = datetime.datetime.now().strftime('%Y%m%d')
    allfiles = os.listdir(os.path.expanduser(datadir))
    allfiles = [x for x in allfiles if 'FILES' not in x]
    allfiles = [x for x in allfiles if tod not in x]

    archuser = thiscfg['archive']['archuser']
    archkeyfile = thiscfg['archive']['archkey']
    archfldr = thiscfg['archive']['archfldr']
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.RSAKey.from_private_key_file(os.path.expanduser(archkeyfile))
    try:
        ssh_client.connect(archserver, username=archuser, pkey=pkey, look_for_keys=False)
        ftp_client = ssh_client.open_sftp()
        targfldr = os.path.join(archfldr, tod[:4])
        flist = ftp_client.listdir(targfldr)
        flist = [x for x in flist if '.zip' in x]
        flist = [x.replace('.zip','') for x in flist]
    except:
        flist = []
    dirnames = [x for x in allfiles if x in flist]
    return dirnames


def pushFilesToUpload(datadir, bucket, awskey, awssec):
    """
    Upload current list of folders/files to be archived back to AWS

    Parameters
        datadir [string] datadir to save in
        bucket  [string] target bucket
        awskey  [string] aws access key
        awssec  [string] aws secret key
    """
    conn = boto3.Session(aws_access_key_id=awskey, aws_secret_access_key=awssec) 
    s3 = conn.client('s3')
    s3.upload_file(os.path.join(datadir, 'FILES_TO_UPLOAD.inf'), bucket, 'auroracam/FILES_TO_UPLOAD.inf')
    return 


def getFreeSpace():
    free = shutil.disk_usage('/').free
    freekb = free/1024
    return freekb


def getNeededSpace():
    """
    Calculate space required for next 24 hours of operation. 
    each jpg is about 100kB, and we capture about 20,000 per day - about one every 4 seconds 
    plus extra for the timelapses and tarballs, and a bit of overhead 
    """
    jpgspace = 20000 * 100 # 100 kB per file
    mp4space = 100 * 1024  # 100 MB
    tarballspace = 1500 * 1024 # 1.5 GB 
    extraspace = 50 * 1024 # 50 MB extra just in case
    reqspace = jpgspace + extraspace + tarballspace + mp4space
    return reqspace


def getDeletableFiles(datadir, daystokeep=3, filestokeep=None):
    """
    Get a list of files and folders that can be deleted

    Parameters:
        datadir     [string] - the root folder containing the data files eg ~/RMS_data/auroracam
        daystokeep  [int]    - number of recent days to keep and consider not deletable
        filestokeep [string] - a list of files or folders we want to archive before deleting
    """
    tod = datetime.datetime.now().strftime('%Y%m%d')
    allfiles = os.listdir(datadir)
    allfiles = [x for x in allfiles if 'FILES' not in x]
    allfiles = [x for x in allfiles if tod not in x]
    origallfiles = allfiles
    for d in range(1,daystokeep):
        yest = (datetime.datetime.now() - datetime.timedelta(days=d)).strftime('%Y%m%d')
        allfiles = [x for x in allfiles if yest not in x]
    for patt in filestokeep:
        toarch = [x for x in origallfiles if patt.strip() in x]
        allfiles += toarch
    allfiles.sort()
    return allfiles


def compressAndUpload(datadir, thisfile, thiscfg):
    """
    Compress and upload data.
    If thisfile is a folder name, the folder is compressed into a zip archive.
    The zipped archive is then uploaded to the target server and location. 
    The year is postpended to the target folder, so that data will be sorted by year on the server.
    The zip archive is deleted after upload. 

    Parameters:
        datadir     [string] - the root folder containing the data files eg ~/RMS_data/auroracam
        thisfile    [string] - the name of the file or folder to process
        archserver  [string] - target server to archive files to
        archfolder  [string] - target location on server. The current year will be appended to this. 

    
    """
    if '.zip' in thisfile or '.tgz' in thisfile:
        pass
    else:
        log.info(f'Archiving {thisfile}')
        zfname = os.path.join(datadir, thisfile)
        shutil.make_archive(zfname,'zip',zfname)
    log.info(f'uploading {thisfile}')
    archserver = thiscfg['archive']['archserver']
    archuser = thiscfg['archive']['archuser']
    archkeyfile = thiscfg['archive']['archkey']
    archfldr = thiscfg['archive']['archfldr']
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.RSAKey.from_private_key_file(os.path.expanduser(archkeyfile))
    try:
        ssh_client.connect(archserver, username=archuser, pkey=pkey, look_for_keys=False)
        ftp_client = ssh_client.open_sftp()
        uploadfile = os.path.join(archfldr, thisfile[:4], thisfile +'.zip')
        try:
            ftp_client.put(zfname + '.zip', uploadfile)
            try:
                filestat = ftp_client.stat(uploadfile)
                log.info(f'uploaded {filestat.st_size} bytes')
                os.remove(zfname + '.zip')
            except Exception as e:
                log.error(f'unable to upload {thisfile}')
                log.info(e, exc_info=True)
                return False
        except Exception as e:
            log.error(f'unable to upload {thisfile}')
            log.info(e, exc_info=True)
            return False
        ftp_client.close()
        ssh_client.close()
        return True
    except Exception as e:
        log.warning(f'connection to {archserver} failed')
        log.info(e, exc_info=True)
        return False


def freeUpSpace(thiscfg):
    """
    Free up space by deleting older data. 
    Free space is checked and required space determined. The routine then obtains a list
    of folders that the user has marked as of interest and to be saved, and  a list 
    of files & folders in the datadir which might be deletable. By default, the last three 
    days worth of data will be retained unless space is required. 

    We then loop through the list of deletable files and folders, checking if they're marked
    as to be archived and compressing and archiving if needed. Freespace is then checked
    and if insufficient, the folder or file is deleted. This continues till there's sufficient space.

    Parameters:
        thiscfg     [object] - json object containing the configuration 
    """
    uid = platform.uname()[1]
    datadir = os.path.expanduser(thiscfg['auroracam']['datadir'])
    s3 = None
    uploadloc = None
    filestoupload = None
    uploadloc = thiscfg['uploads']['s3uploadloc']
    if uploadloc[:5] == 's3://':
        log.info(f'getting list of files to upload from {uploadloc}')
        # try to retrieve an AWS key from the sftp server
        s3 = getAWSConn(thiscfg, uid, uid)
        filestoupload = getFilesToUpload(datadir, uploadloc[5:], s3)
    else:
        filestoupload = getListOfNew(datadir, thiscfg)
    log.info(f'want to keep {filestoupload}')
    freekb = getFreeSpace()
    reqkb = getNeededSpace()
    log.info(f'need {reqkb/1024/1024:.3f} GB, have {freekb/1024/1024:.3f} GB')
    log.info(f'archiving to {thiscfg["archive"]["archserver"]}:{thiscfg["archive"]["archfl;dr"]}')
    filelist = getDeletableFiles(datadir, daystokeep=3, filestokeep=filestoupload)
    for thisfile in filelist:
        for origpatt in filestoupload:
            patt = origpatt.strip()
            if patt in thisfile and len(patt) > 8:
                if compressAndUpload(datadir, thisfile, thiscfg):
                    while origpatt in filestoupload:
                        filestoupload.remove(origpatt)
                    open(os.path.join(datadir, 'FILES_TO_UPLOAD.inf'), 'w').writelines(filestoupload)                        
                    newfree = getFreeSpace()
                    if newfree < reqkb:
                        shutil.rmtree(os.path.join(datadir, thisfile))
                else:
                    print(f'problem compressing or uploading {thisfile}')
        newfree = getFreeSpace()
        if os.path.isfile(os.path.join(datadir, thisfile)):
            if newfree < reqkb:
                log.info(f'deleting {thisfile}')
                os.remove(os.path.join(datadir, thisfile))
        else:
            if newfree < reqkb:
                log.info(f'removing folder {thisfile}')
                try:
                    shutil.rmtree(os.path.join(datadir, thisfile))
                except:
                    log.warning(f'folder {thisfile} already pruned')
                try:
                    shutil.rmtree(os.path.join(datadir, thisfile))
                except:
                    log.warning(f'folder {thisfile} already pruned')
    newfree = getFreeSpace()
    if s3:
        s3.upload_file(os.path.join(datadir, 'FILES_TO_UPLOAD.inf'), uploadloc[5:], 'auroracam/FILES_TO_UPLOAD.inf')
    log.info(f'freed {(newfree - freekb)/1024/1024:.3f} GB, have {newfree/1024/1024:.3f} GB')
    return 


if __name__ == '__main__':
    thiscfg = configparser.ConfigParser()
    local_path = os.path.dirname(os.path.abspath(__file__))
    thiscfg.read(os.path.join(local_path, 'config.ini'))
    setupLogging(thiscfg, 'archive_')
    freeUpSpace(thiscfg)
