# various utils for my allsky cam

import os
import datetime 
import glob 
import shutil
import configparser
import paramiko
from paramiko.config import SSHConfig


def getInterestingFiles(capdir, dt1, dt2):
    # a function to get all fits files between two date/time ranges
    t1 = datetime.datetime.strptime(dt1, '%Y%m%d_%H%M%S').timestamp()
    t2 = datetime.datetime.strptime(dt2, '%Y%m%d_%H%M%S').timestamp()
    capdir = os.path.expanduser(capdir)
    currdir = os.path.basename(os.path.normpath(capdir))
    tmp_folder = os.path.join('/tmp/', currdir)
    os.makedirs(tmp_folder, exist_ok=True)
    for ff in glob.glob(os.path.join(capdir, 'image-*.jpg')):
        fftime = os.path.getmtime(ff)
        if fftime > t1 and fftime <=t2:
            shutil.copyfile(ff, os.path.join(tmp_folder, os.path.basename(ff)))    
    zipf = shutil.make_archive(tmp_folder, 'zip', root_dir = tmp_folder, base_dir=tmp_folder)
    localcfg = configparser.ConfigParser()
    srcdir = os.path.split(os.path.abspath(__file__))[0]
    localcfg.read(os.path.join(srcdir, 'config.ini'))
    sshconfig=SSHConfig.from_path(os.path.expanduser('~/.ssh/config'))
    sitecfg = sshconfig.lookup(localcfg['backup']['target'])  
    pkey = paramiko.RSAKey.from_private_key_file(sitecfg['identityfile'][0])  
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(sitecfg['hostname'], username=sitecfg['user'], pkey=pkey, look_for_keys=False)
    ftp = ssh_client.open_sftp()
    rempath = f'{localcfg["backup"]["remotepath"]}/{currdir[0:4]}/{currdir}_saved.zip'
    ftp.put(zipf, rempath)
    ftp.close()
    ssh_client.close()
    shutil.rmtree(tmp_folder)
    os.remove(zipf)
    return 
