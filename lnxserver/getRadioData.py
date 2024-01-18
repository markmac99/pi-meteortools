#
# Copyright (C) Mark McIntyre
#
# script to copy radio detections to my archive server

import os
from time import time
import pandas as pd
from paramiko import SSHClient, AutoAddPolicy


def archiveRadioData(srchost, srcuser, passwd):
    targdir = os.getenv('TARGETDIR', default='/data3/astrodata/meteorcam/radio/')
    rempath = os.getenv('SRCDIR', default='c:/spectrum')
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    ssh_client.connect(srchost, username=srcuser, password=passwd)
    ftp_client = ssh_client.open_sftp()
    os.makedirs(os.path.join(targdir,'logs'), exist_ok=True)
    localflist = os.listdir(os.path.join(targdir, 'logs'))
    files = pd.DataFrame([attr.__dict__ for attr in ftp_client.listdir_attr(rempath + '/logs')]).sort_values("st_mtime", ascending=False)
    tnow = time()
    print('checking...')
    gotcount = 0
    for _, rw in files.iterrows():
        remf = rw.filename
        remmtime = rw.st_mtime
        locfname = os.path.join(targdir, 'logs', remf)
        remfname = rempath + '/logs/' + remf
        if (tnow - remmtime) > 86400*7:
            continue
        if remf not in localflist:
            print(f'getting {remf}')
            ftp_client.get(remfname, locfname)
            gotcount +=1 
        else:
            locmtime = os.path.getmtime(locfname)
            if remmtime > locmtime:
                print(f'getting {remf}')
                ftp_client.get(remfname, locfname)
                gotcount +=1 
    print(f'retrieved {gotcount} files')
    return


if __name__ == '__main__':
    srchost = os.getenv('SRCHOST', default='astro3')
    srcuser = os.getenv('SRCUSER', default='dataxfer')
    passwd = open(os.getenv('PASSFILE'), 'r').readlines()[0].strip()
    archiveRadioData(srchost, srcuser, passwd)
