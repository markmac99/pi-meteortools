# 
# python script thats called when the nightly run completes
# requires
# ~/.ssh/gmailpass - plaintext file containing gmail password
# ~/.ssh/keyfile - plaintext file containing S3 keys or SSH private key for 
# upload to S3 or website. filename configurable in config file
#
#

import os
import sys
import glob
import shutil
import configparser
import logging
import datetime

import RMS.ConfigReader as cr
import Utils.TrackStack as ts
import Utils.StackFFs as sff
from RMS.Logger import initLogging

import boto3

sys.path.append(os.path.split(os.path.abspath(__file__))[0])
from annotatateImage import annotateImage
import sendAnEmail as em
import sendToYoutube as stu


def copyAndStack(arch_dir, srcdir, log):
    # copy FFs for stacking
    idfile = '/home/pi/.ssh/markskey.pem'
    user = 'bitnami'
    hn = '3.9.128.14'

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
    numffs = glob.glob1(outdir, 'FF*.fits')
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
        mthfile = os.path.join(outdir, '{:s}_{:04d}{:02d}.jpg'.format(camid, now.year, now.month))
        targdir = 'data/mjmm-data/{}/stacks/'.format(camid)
        cmdline = 'scp -i {:s} {:s} {:s}@{:s}:{:s}/{}'.format(idfile, fn, user, hn, targdir, mthfile)
        os.system(cmdline)
    else:
        log.info('no stack to upload')


def rmsExternal(cap_dir, arch_dir, config):
    rebootlockfile = os.path.join(config.data_dir, config.reboot_lock_file)
    with open(rebootlockfile, 'w') as f:
        f.write('1')

    # clear existing log handlers
    log = logging.getLogger("logger")
    while log.hasHandlers():
        log.removeHandler(log.handlers[0])
        
    initLogging(config, 'tackley_')
    log.info('ukmon external script started')

    log.info('reading local config')
    srcdir = os.path.split(os.path.abspath(__file__))[0]
    localcfg = configparser.ConfigParser()
    localcfg.read(os.path.join(srcdir, 'config.ini'))
    sys.path.append(srcdir)

    hname = os.uname()[1]

    extramsg = 'Notes:\n'
    
    mp4name = os.path.basename(cap_dir) + '.mp4'
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
                    stu.main(msg, os.path.join(arch_dir, mp4name))
                else:
                    log.info('already uploaded {:s}'.format(mp4name))
                    
                with open(os.path.join(srcdir, '.ytdone'), 'w') as f:
                    f.write(mp4name)
        except Exception:
            errmsg = 'unable to upload timelapse'
            log.info(errmsg)
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
            s3.meta.client.upload_file(fn, target, outf)
        else:
            print('uploading to website')
            user = localcfg['postprocess']['user']
            mp4dir = localcfg['postprocess']['mp4dir']
            cmdline = 'ssh -i {:s}  {:s}@{:s} mkdir {:s}/{:s}/{:s}'.format(idfile, user, hn, mp4dir, stn, yymm)
            os.system(cmdline)
            cmdline = 'scp -i {:s} {:s} {:s}@{:s}:{:s}/{:s}/{:s}'.format(idfile, fn, user, hn, mp4dir, stn, yymm)
            os.system(cmdline)

    # email a summary to the mailrecip

    logdir = os.path.expanduser(os.path.join(config.data_dir, config.log_dir))
    splits = os.path.basename(arch_dir).split('_')
    curdt = splits[1]
    logname=os.path.join(logdir, 'log_' + splits[1] + '_' + '*.log*')
    logfs = glob.glob(logname)
    total = 0
    for f in logfs:
        with open(f,'r') as fi:
            sl = fi.readlines()
            for line in sl:
                if 'TOTAL' in line:
                    ss = line.split(' ')
                    total = total + int(ss[4])

    em.sendDailyMail(localcfg, hname, curdt, total, extramsg)

    try:
        ts.trackStack(arch_dir, config)
    except Exception:
        pass
    
    copyAndStack(arch_dir, srcdir, log)

    os.remove(rebootlockfile)

    if os.path.exists(os.path.join(srcdir, 'doistream')):
        log.info('doing istream')
        sys.path.append('/home/pi/source/RMS/iStream')
        import iStream as istr
        istr.rmsExternal(cap_dir, arch_dir, config)
    else:
        log.info('not doing istream')
    return


if __name__ == '__main__':
    hname = os.uname()[1]
    if len(sys.argv) < 1:
        if hname == 'meteorpi':
            cap_dir = '/home/pi/RMS_data/CapturedFiles/UK0006_20210130_172616_214463'
            arch_dir = '/home/pi/RMS_data/ArchivedFiles/UK0006_20210130_172616_214463'
        else:
            cap_dir = '/home/pi/RMS_data/CapturedFiles/UK000F_20210128_172253_791467'
            arch_dir = '/home/pi/RMS_data/ArchivedFiles/UK000F_20210128_172253_791467'
    else:
        cap_dir = os.path.join('/home/pi/RMS_data/CapturedFiles/', sys.argv[1])
        arch_dir = os.path.join('/home/pi/RMS_data/ArchivedFiles/', sys.argv[1])

    config = cr.parse(".config")

    rmsExternal(cap_dir, arch_dir, config)
