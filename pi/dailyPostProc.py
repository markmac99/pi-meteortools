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
import shutil
import configparser
import logging
import datetime
import time

import RMS.ConfigReader as cr
import Utils.StackFFs as sff
from RMS.Logger import initLogging

import boto3

sys.path.append(os.path.split(os.path.abspath(__file__))[0])
from annotateImage import annotateImage
import sendAnEmail as em
import sendToYoutube as stu
import sendToMQTT as mqs


def copyAndStack(arch_dir, srcdir, log, localcfg):
    # copy FFs for stacking
    idfile = localcfg['postprocess']['webid'] # /home/pi/.ssh/markskey.pem'
    user = localcfg['postprocess']['user']  # 'bitnami'
    hn = localcfg['postprocess']['webserver'] # '3.9.128.14'

    outdir = os.path.join(srcdir, 'tmp')
    camid = os.path.basename(arch_dir).split('_')[0]
    fn = os.path.join(outdir, '{}_latest.jpg'.format(camid))

    now = datetime.datetime.now()
    if now.day == 1:
        log.info('clearing last months data')
        cmdline = 'rm {}/*.fits {}/*.jpg'.format(outdir, outdir)
        os.system(cmdline)

    log.info('removing previous night stack')    
    if os.path.isfile(fn):
        os.remove(fn)
    
    log.info('getting FITS files')
    ffs = glob.glob1(arch_dir, 'FF*.fits')
    for ff in ffs:
        srcfil = os.path.join(arch_dir, ff)        
        shutil.copy2(srcfil, outdir)

    log.info('creating stack')
    sff.stackFFs(outdir, 'jpg',subavg=True, filter_bright=True)
    ffs = glob.glob1(outdir, 'FF*.fits')
    numffs = len(ffs)
    now = datetime.datetime.now()
    title = '{} {}'.format(camid, now.strftime('%Y-%m-%d'))

    jpgs = glob.glob1(outdir, '*.jpg')
    if len(jpgs) > 0:
        log.info('uploading stack')
        lateststack = os.path.join(outdir, '{}_latest.jpg'.format(camid))
        os.rename(os.path.join(outdir, jpgs[0]), lateststack)
        annotateImage(lateststack, title, numffs)
        targdir = 'data/meteors/'
        cmdline = 'scp -i {:s} {:s} {:s}@{:s}:{:s}'.format(idfile, fn, user, hn, targdir)
        os.system(cmdline)
        mthfile = '{:s}_{:04d}{:02d}.jpg'.format(camid, now.year, now.month)
        targdir = 'data/mjmm-data/{}/stacks'.format(camid)
        cmdline = 'scp -i {:s} {:s} {:s}@{:s}:{:s}/{}'.format(idfile, fn, user, hn, targdir, mthfile)
        os.system(cmdline)
    else:
        log.info('no stack to upload')


def reStackAndPush(arch_dir):
    config = cr.parse('.config')
    log = logging.getLogger("logger")
    initLogging(config, 'tackley_')
    localcfg = configparser.ConfigParser()
    srcdir = os.path.split(os.path.abspath(__file__))[0]
    localcfg.read(os.path.join(srcdir, 'config.ini'))
    copyAndStack(arch_dir, srcdir, log, localcfg)


def rmsExternal(cap_dir, arch_dir, config):
    rebootlockfile = os.path.join(config.data_dir, config.reboot_lock_file)
    with open(rebootlockfile, 'w') as f:
        f.write('1')

    # clear existing log handlers
    log = logging.getLogger("logger")
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

    extramsg = 'Notes:\n'
    
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
            extramsg = extramsg + errmsg + '\n'

    # upload the MP4 to S3 or a website
    if int(localcfg['postprocess']['upload']) == 1:
        hn = localcfg['postprocess']['host']
        fn = os.path.join(arch_dir, mp4name)
        splits = mp4name.split('_')
        stn = splits[0]
        yymm = splits[1]
        yymm = yymm[:6]
        idfile = os.path.expanduser(localcfg['postprocess']['idfile'])
        if hn[:3] == 's3:':
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
                s3.meta.client.upload_file(fn, target, outf)
            except Exception as e:
                print('upload to S3 failed')
                log.info(e, exc_info=True)
        else:
            log.info('uploading to website')
            user = localcfg['postprocess']['user']
            mp4dir = localcfg['postprocess']['mp4dir']
            cmdline = 'ssh -i {:s}  {:s}@{:s} mkdir {:s}/{:s}/{:s}'.format(idfile, user, hn, mp4dir, stn, yymm)
            os.system(cmdline)
            cmdline = 'scp -i {:s} {:s} {:s}@{:s}:{:s}/{:s}/{:s}'.format(idfile, fn, user, hn, mp4dir, stn, yymm)
            os.system(cmdline)

    # email a summary to the mailrecip

    logdir = os.path.expanduser(os.path.join(config.data_dir, config.log_dir))
    logfs = glob.glob(os.path.join(logdir, 'log*.log*'))
    logfs.sort(key=lambda x: os.path.getmtime(x))
    with open(logfs[-1],'r') as fi:
        sl = fi.readlines()
    totli = [li for li in sl if 'TOTAL' in li]
    total = 0
    if len(totli) > 0:
        total = totli[0].split(' ')[4]

    if len(localcfg['mqtt']['broker']) > 1:
        log.info('sending to MQ')
        try:
            mqs.sendToMqtt(config)
        except Exception as e:
            log.warning('problem sending to MQTT')
            log.info(e, exc_info=True)

    if len(localcfg['postprocess']['mailrecip']) > 1:
        log.info('sending email')
        splits = os.path.basename(arch_dir).split('_')
        curdt = splits[1]
        try: 
            em.sendDailyMail(localcfg, hname, curdt, total, extramsg, log)
        except Exception as e:
            log.warning('problem sending email')
            log.info(e, exc_info=True)

    if os.path.exists(os.path.join(srcdir, 'doistream')):
        log.info('doing istream')

        # clear log handlers as we want istrastream in its own logfile
        while len(log.handlers) > 0:
            log.removeHandler(log.handlers[0])

        sys.path.append(os.path.expanduser('~/source/RMS/iStream'))
        import iStream as istr
        istr.rmsExternal(cap_dir, arch_dir, config)
    else:
        # only remove this if we are finished with processing
        os.remove(rebootlockfile)
        log.info('not doing istream')

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
