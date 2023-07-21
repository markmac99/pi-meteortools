# 
# python script thats called when the nightly run completes
# requires
# ~/.ssh/gmailpass - plaintext file containing gmail password
# ~/.ssh/keyfile - plaintext file containing S3 keys or SSH private key for 
# upload to S3 or website. filename configurable in config file
#
# Copyright (C) Mark McIntyre
#
#

import os
import sys
import glob
import configparser
import logging
import time
import shutil
import datetime 
from dateutil.relativedelta import relativedelta
import paramiko
from paramiko.config import SSHConfig


import RMS.ConfigReader as cr
from RMS.Logger import initLogging
from Utils.StackFFs import stackFFs
from RMS.Routines import MaskImage
from Utils.TrackStack import trackStack

from ukmon_meteortools.utils import annotateImage
import boto3

sys.path.append(os.path.split(os.path.abspath(__file__))[0])
import sendToYoutube as stu # noqa:E402
import sendToMQTT as mqs # noqa:E402


log = logging.getLogger("logger")


def pushLatestStack(targetname, imgname):
    config=SSHConfig.from_path(os.path.expanduser('~/.ssh/config'))
    sitecfg = config.lookup(targetname)
    if 'user' not in sitecfg.keys():
        log.warning(f'unable to connect to {targetname} - no entry in ssh config file')
        return 
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.RSAKey.from_private_key_file(sitecfg['identityfile'][0])
    ssh_client.connect(sitecfg['hostname'], username=sitecfg['user'], pkey=pkey, look_for_keys=False)
    ftp_client = ssh_client.open_sftp()
    _, fname = os.path.split(imgname)
    camid = fname[:6]
    if os.path.isfile(imgname):
        ftp_client.put(imgname, f'data/meteors/{camid}_latest.jpg')
        log.info(f'uploaded {fname} to {targetname}')
    else:
        log.warning(f'file {imgname} not found')
    return 


def copyMLRejects(cap_dir, arch_dir):
    ftplist = [f for f in glob.glob(os.path.join(arch_dir,'FTPdetectinfo*.txt')) if 'backup' not in f and 'uncalibrated' not in f]
    detlist = [f for f in ftplist if 'unfiltered' not in f]
    detlist = detlist[0]
    uflist = [f for f in ftplist if 'unfiltered' in f]
    uflist = uflist[0]
    
    dets = [li.strip() for li in open(detlist,'r').readlines() if 'FF_' in li]
    ufdets = [li.strip() for li in open(uflist,'r').readlines() if 'FF_' in li]
    rejs = [li for li in ufdets if li not in dets]
    for ff_file in rejs:
        srcfile = os.path.join(cap_dir, ff_file)
        trgfile = os.path.join(arch_dir, ff_file)
        if os.path.isfile(srcfile) and not os.path.isfile(trgfile):
            log.info(f'copying reject {os.path.basename(srcfile)}')
            shutil.copyfile(srcfile, trgfile)
    return 


def monthlyStack(cfg, arch_dir, localcfg):
    currdir = os.path.basename(os.path.normpath(arch_dir))
    lastmthstr = currdir[:7] + (datetime.datetime.strptime(currdir[7:13], '%Y%m')+ relativedelta(months=-1)).strftime('%Y%m')
    tmpdir = os.path.join(cfg.data_dir, 'tmpstack')
    os.makedirs(tmpdir, exist_ok=True)
    # clear out last months data if present
    oldfflist = glob.glob(os.path.join(tmpdir, '*.fits'))
    for ff in oldfflist:
        if lastmthstr in ff:
            os.remove(ff)
    oldjpgs = glob.glob(os.path.join(tmpdir, '*.jpg'))
    for oldjpg in oldjpgs:
        os.remove(oldjpg)
    # copy most recent fits files
    flist = glob.glob(f'{arch_dir}/*.fits')
    for ff in flist:
        targ = os.path.join(tmpdir, os.path.basename(ff))
        if not os.path.isfile(targ):
            log.info(f'copying {os.path.basename(ff)} for stacking')
            shutil.copyfile(ff, targ)
    # copy the mask if not already there
    maskfile = os.path.join(tmpdir, 'mask.bmp')
    if not os.path.isfile(maskfile):
        currmaskf = os.path.join(arch_dir, 'mask.bmp')
        if os.path.isfile(currmaskf):
            shutil.copyfile(currmaskf, maskfile)
    mask = MaskImage.loadMask(maskfile)
    # stack files. Flat is not used if subavg is true
    stackFFs(tmpdir, file_format='jpg', subavg=True, filter_bright=True, mask=mask) 
    jpgfile = glob.glob(os.path.join(tmpdir, '*.jpg'))
    if len(jpgfile) > 0:
        stn = cfg.stationID
        flist = glob.glob(os.path.join(tmpdir, '*.fits'))
        annotateImage(jpgfile[0], stn, metcount=len(flist), rundate=currdir[7:13])
        targ = os.path.join(arch_dir, currdir[:13]+'.jpg')
        shutil.copyfile(jpgfile[0], targ)
        idfile = os.path.expanduser(localcfg['postprocess']['idfile'])
        hn = localcfg['postprocess']['host']
        if hn[:3] == 's3:':
            log.info('uploading to {:s}/{:s}/{:s}'.format(hn, stn, 'stacks'))
            with open(idfile, 'r') as f:
                li = f.readline()
                key = li.split('=')[1].rstrip().strip('"')
                li = f.readline()
                secret = li.split('=')[1].rstrip().strip('"')
            s3 = boto3.resource('s3', aws_access_key_id = key, aws_secret_access_key = secret, region_name='eu-west-2')
            target=hn[5:]
            outf = '{:s}/stacks/{:s}'.format(stn, currdir[:13]+'.jpg')
            try: 
                s3.meta.client.upload_file(jpgfile[0], target, outf, ExtraArgs ={'ContentType': 'image/jpg'})
            except Exception as e:
                log.warning('upload to S3 failed')
                log.info(e, exc_info=True)
        else:
            log.info('target is not s3, not uploading monthly stack')
        webserver = localcfg['postprocess']['webserver']
        pushLatestStack(webserver, targ)
    return     


def doTrackStack(arch_dir, cfg, localcfg):
    trackStack([arch_dir], cfg, draw_constellations=True, hide_plot=True, background_compensation=False)
    tflist = glob.glob(os.path.join(arch_dir, '*_track_stack.jpg'))
    if len(tflist) > 0:
        trackfile = tflist[0]
        currdir = os.path.basename(os.path.normpath(arch_dir))
        lis = open(os.path.join(arch_dir, 'FTPdetectinfo_'+currdir+'.txt'), 'r').readlines()
        metcount = lis[0].split('=')[1].strip()
        currdir = os.path.basename(os.path.normpath(arch_dir))
        annotateImage(trackfile, cfg.stationID, int(metcount), currdir[7:15])
        idfile = os.path.expanduser(localcfg['postprocess']['idfile'])
        hn = localcfg['postprocess']['host']
        if hn[:3] == 's3:':
            log.info('uploading to {:s}/{:s}/{:s}'.format(hn, cfg.stationID, 'trackstacks'))
            with open(idfile, 'r') as f:
                li = f.readline()
                key = li.split('=')[1].rstrip().strip('"')
                li = f.readline()
                secret = li.split('=')[1].rstrip().strip('"')
            s3 = boto3.resource('s3', aws_access_key_id = key, aws_secret_access_key = secret, region_name='eu-west-2')
            target=hn[5:]
            outf = f'{cfg.stationID}/trackstacks/{os.path.basename(trackfile)[:15]}.jpg'
            try: 
                s3.meta.client.upload_file(trackfile, target, outf, ExtraArgs ={'ContentType': 'image/jpg'})
            except Exception as e:
                log.warning('upload to S3 failed')
                log.info(e, exc_info=True)
        else:
            log.info('target is not s3, not uploading monthly stack')

    return 


def rmsExternal(cap_dir, arch_dir, config):
    rebootlockfile = os.path.join(config.data_dir, config.reboot_lock_file)
    with open(rebootlockfile, 'w') as f:
        f.write('1')

    # clear existing log handlers
    while len(log.handlers) > 0:
        log.removeHandler(log.handlers[0])
        
    initLogging(config, 'tackley_')
    log.info('tackley external script started')

    log.info('reading local config')
    srcdir = os.path.split(os.path.abspath(__file__))[0]
    localcfg = configparser.ConfigParser()
    localcfg.read(os.path.join(srcdir, 'config.ini'))
    sys.path.append(srcdir)

    hname = os.uname()[1][:6]

    # create monthly stack
    log.info('creating monthly tack')
    monthlyStack(config, arch_dir, localcfg)
    # create trackstack
    log.info('creating trackstack')
    doTrackStack(arch_dir, config, localcfg)

    mp4name = os.path.basename(cap_dir) + '_timelapse.mp4'
    if os.path.exists(os.path.join(srcdir, 'token.pickle')):
        # upload mp4 to youtube
        try: 
            if not os.path.isfile(os.path.join(srcdir, '.ytdone')):
                with open(os.path.join(srcdir, '.ytdone'), 'w') as f:
                    f.write('dummy\n')

            with open(os.path.join(srcdir, '.ytdone'), 'r') as f:
                line = f.readline().rstrip()
                if line != mp4name:
                    tod = mp4name.split('_')[1]
                    tod = tod[:4] +'-'+ tod[4:6] + '-' + tod[6:8]
                    msg = '{:s} timelapse for {:s}'.format(hname, tod)
                    log.info('uploading {:s} to youtube'.format(mp4name))
                    for retries in range(5):
                        if stu.main(msg, os.path.join(arch_dir, mp4name)) == 0:
                            break
                        else:
                            time.sleep(10)
                else:
                    log.info('already uploaded {:s}'.format(mp4name))
                    
                with open(os.path.join(srcdir, '.ytdone'), 'w') as f:
                    f.write(mp4name)
        except Exception as e:
            errmsg = 'unable to upload timelapse'
            log.info(errmsg)
            log.info(e, exc_info=True)
    # copy the ML rejected files
    copyMLRejects(cap_dir, arch_dir)
    
    # upload the MP4 to S3 or a website
    if int(localcfg['postprocess']['upload']) == 1:
        hn = localcfg['postprocess']['host']
        fn = os.path.join(arch_dir, mp4name)
        splits = mp4name.split('_')
        stn = splits[0]
        yymm = splits[1]
        yymm = yymm[:6]
        idfile = os.path.expanduser(localcfg['postprocess']['idfile'])
        log.info('uploading to {:s}/{:s}/{:s}'.format(hn, stn, yymm))

        with open(idfile, 'r') as f:
            li = f.readline()
            key = li.split('=')[1].rstrip().strip('"')
            li = f.readline()
            secret = li.split('=')[1].rstrip().strip('"')

        s3 = boto3.resource('s3', aws_access_key_id = key, aws_secret_access_key = secret, 
            region_name='eu-west-2')
        target=hn[5:]
        outf = '{:s}/{:s}/{:s}'.format(stn, yymm, mp4name)
        try: 
            s3.meta.client.upload_file(fn, target, outf, ExtraArgs ={'ContentType': 'video/mp4'})
        except Exception as e:
            log.warning('upload to S3 failed')
            log.info(e, exc_info=True)

    if len(localcfg['mqtt']['broker']) > 1:
        log.info('sending to MQ')
        try:
            mqs.sendToMqtt(config)
        except Exception as e:
            log.warning('problem sending to MQTT')
            log.info(e, exc_info=True)

    os.remove(rebootlockfile)

    # clear log handlers again
    while len(log.handlers) > 0:
        log.removeHandler(log.handlers[0])
    return


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: dailyPostProc.py UK0006_20230318_184715_611839 {optional config file}')
    hname = os.uname()[1]
    if len(sys.argv) > 2: 
        rmscfg = os.path.expanduser(sys.argv[2])
    else:
        rmscfg = os.path.expanduser('~/source/RMS/.config')
    config = cr.parse(rmscfg)
    datadir = config.data_dir
    cap_dir = os.path.join(datadir, 'CapturedFiles', sys.argv[1])
    arch_dir = os.path.join(datadir, 'ArchivedFiles', sys.argv[1])
  
    rmsExternal(cap_dir, arch_dir, config)
