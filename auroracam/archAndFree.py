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
import paramiko
import logging

from grabImage import setupLogging

log = logging.getLogger("logger")


def getFilesToUpload(datadir):
    dirnames = open(os.path.join(datadir, 'FILES_TO_UPLOAD.inf'), 'r').readlines()
    if len(dirnames) == 0:
        return False
    return dirnames


def saveFilesToUpload(datadir, dirs):
    open(os.path.join(datadir, 'FILES_TO_UPLOAD.inf'), 'w').writelines(dirs)
    return 


def getFreeSpace():
    free = shutil.disk_usage('/').free
    freekb = free/1024
    return freekb


def getNeededSpace():
    #each jpg is about 100kB, and we capture about 20,000 per day - about one every 4 seconds
    # plus extra for the timelapses and tarballs, and a bit of overhead
    jpgspace = 20000 * 100 # 100 kB per file
    mp4space = 100 * 1024  # 100 MB
    tarballspace = 1500 * 1024 # 1.5 GB 
    extraspace = 50 * 1024 # 50 MB extra just in case
    reqspace = jpgspace + extraspace + tarballspace + mp4space
    return reqspace


def getDeletableFiles(datadir, daystokeep=3):
    tod = datetime.datetime.now().strftime('%Y%m%d')
    allfiles = os.listdir(datadir)
    allfiles = [x for x in allfiles if 'FILES' not in x]
    allfiles = [x for x in allfiles if tod not in x]
    for d in range(1,daystokeep):
        yest = (datetime.datetime.now() - datetime.timedelta(days=d)).strftime('%Y%m%d')
        allfiles = [x for x in allfiles if yest not in x]
    allfiles.sort()
    return allfiles


def compressAndUpload(datadir, thisfile, archserver, archfldr):
    if '.zip' in thisfile or '.tgz' in thisfile:
        pass
    else:
        log.info(f'Archiving {thisfile}')
        zfname = os.path.join(datadir, thisfile)
        shutil.make_archive(zfname,'zip',zfname)
    log.info(f'uploading {thisfile}')
    config=paramiko.config.SSHConfig.from_path(os.path.expanduser('~/.ssh/config'))
    sitecfg = config.lookup(archserver)
    if 'user' not in sitecfg.keys():
        log.warning(f'unable to connect to {archserver} - no entry in ssh config file')
        return False
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.RSAKey.from_private_key_file(sitecfg['identityfile'][0])
    try:
        ssh_client.connect(sitecfg['hostname'], username=sitecfg['user'], pkey=pkey, look_for_keys=False)
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
        log.warning(f'connection to {sitecfg["hostname"]} failed')
        log.info(e, exc_info=True)
        return False


def freeUpSpace(datadir, archserver, archfldr):
    freekb = getFreeSpace()
    reqkb = getNeededSpace()
    log.info(f'need {reqkb/1024/1024:.3f} GB, have {freekb/1024/1024:.3f} GB')
    log.info(f'archiving to {archserver}{archfldr}')     
    filelist = getDeletableFiles(datadir)
    filestoupload = getFilesToUpload(datadir)
    log.info(f'want to keep {filestoupload}')
    for thisfile in filelist:
        for patt in filestoupload:
            patt = patt.strip()
            if patt in thisfile:
                if compressAndUpload(datadir, thisfile, archserver, archfldr):
                    filestoupload.remove(patt)
                    saveFilesToUpload(datadir, filestoupload)
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
                shutil.rmtree(os.path.join(datadir, thisfile))
    newfree = getFreeSpace()
    log.info(f'freed {(newfree - freekb)/1024/1024:.3f} GB, have {newfree/1024/1024:.3f} GB')
    return 


if __name__ == '__main__':
    thiscfg = configparser.ConfigParser()
    local_path =os.path.dirname(os.path.abspath(__file__))
    thiscfg.read(os.path.join(local_path, 'config.ini'))

    setupLogging(thiscfg, 'archive_')

    datadir = os.path.expanduser(thiscfg['auroracam']['datadir'])
    archserver = thiscfg['archive']['archserver']
    archfldr = thiscfg['archive']['archfldr']
    freeUpSpace(datadir, archserver, archfldr)
