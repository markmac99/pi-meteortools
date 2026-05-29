# Copyright (C) Mark McIntyre
#
# utility functions

import tempfile
import paramiko
from paramiko.config import SSHConfig
import logging

import RMS.ConfigReader as cr
import os


tackleylog = logging.getLogger('tackleyloger')


def getRMSConfig(statid, localcfg):
    if 'xx' in statid.lower():
        return None
    rmscfg = os.path.expanduser(f'~/source/Stations/{statid}/.config')
    if not os.path.isfile(rmscfg):
        rmscfg = os.path.join(localcfg['postprocess']['rmsdir'], '.config')
    if not os.path.isfile(rmscfg):
        return None
    cfg = cr.parse(os.path.expanduser(rmscfg))
    return cfg


def getAWSKey(servername, remotekeyname, uid=None, sshkeyfile=None):
    """ 
    This function retreives an AWS key/secret for uploading the live image. 
    """
    if uid is None:
        config=SSHConfig.from_path(os.path.expanduser('~/.ssh/config'))
        sitecfg = config.lookup(servername)
        if 'user' not in sitecfg.keys():
            tackleylog.warning(f'unable to connect to {servername} - no entry in ssh config file')
            return 
    else:
        sitecfg={}
        sitecfg['hostname'] = servername
        sitecfg['user'] = uid.lower()
        sitecfg['identityfile'] = [os.path.expanduser(sshkeyfile)]
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.RSAKey.from_private_key_file(sitecfg['identityfile'][0])
    key = ''
    # print(sitecfg)
    try: 
        ssh_client.connect(sitecfg['hostname'], username=sitecfg['user'], pkey=pkey, look_for_keys=False)
        ftp_client = ssh_client.open_sftp()
        try:
            handle, tmpfnam = tempfile.mkstemp()
            ftp_client.get(remotekeyname.lower() + '.csv', tmpfnam)
        except Exception as e:
            tackleylog.error('unable to find AWS key')
            tackleylog.info(e, exc_info=True)
        ftp_client.close()
        try:
            lis = open(tmpfnam, 'r').readlines()
            os.close(handle)
            os.remove(tmpfnam)
            key, sec = lis[1].split(',')
        except Exception as e:
            tackleylog.error('malformed AWS key')
            tackleylog.info(e, exc_info=True)
    except Exception as e:
        tackleylog.error('unable to retrieve AWS key')
        tackleylog.info(e, exc_info=True)
    ssh_client.close()
    if key:
        tackleylog.info('retrieved key details')
        return key.strip(), sec.strip() 
    else: 
        return False, False
