# 
# python script thats called when the nightly run completes
# requires
# ~/.ssh/gmailpass - plaintext file containing gmail password
# ~/.ssh/keyfile - plaintext file containing S3 keys or SSH private key for 
# upload to S3 or website. filename configurable in config file
#
# Copyright (C) Mark McIntyre


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
from PIL import Image, ImageFont, ImageDraw
import tempfile
from crontab import CronTab

import RMS.ConfigReader as cr
from RMS.Logger import initLogging
from Utils.StackFFs import stackFFs
from RMS.Routines import MaskImage
from RMS.DeleteOldObservations import getNightDirs, deleteNightFolders
from Utils.TrackStack import trackStack

from meteortools.utils import annotateImage
from meteortools.utils import sendAnEmail
import boto3

sys.path.append(os.path.split(os.path.abspath(__file__))[0])
import sendToYoutube as stu # noqa:E402
from sendToMQTT import sendToMqtt # noqa:E402
from setExpo import addCrontabEntries as setExpoAddCron # noqa:E402

log = logging.getLogger("logger")


def addCrontabs():
    local_path =os.path.dirname(os.path.abspath(__file__))
    cron = CronTab(user=True)
    for job in cron:
        if 'postMatchStats' in job.command or 'trackStarCount' in job.command \
                or 'logTemperature' in job.command or 'setIPCamExpo' in job.command or 'logToMQTT' in job.command:
            cron.remove(job)
            cron.write()
    job = cron.new(f'{local_path}/postMatchStats.sh >> /dev/null 2>&1')
    job.setall('*/15', '9,10,11,12', '*', '*', '*')
    cron.write()
    job = cron.new(f'{local_path}/trackStarCount.sh >> /dev/null 2>&1')
    job.setall('*/10', '*', '*', '*', '*')
    cron.write()
    job = cron.new(f'{local_path}/logToMQTT.sh >> /dev/null 2>&1')
    job.setall('*/5', '*', '*', '*', '*')
    cron.write()
    cfg = configparser.ConfigParser(inline_comment_prefixes=';')
    rmsdir = os.path.expanduser(os.getenv('RMSDIR', default='~/source/RMS'))
    cfg.read(os.path.join(rmsdir,'.config'))
    ipaddr = cfg['Capture']['device'].split('/')[2].split(':')[0]
    setExpoAddCron(ipaddr, cfg)
    return 


def getAWSKey(servername, remotekeyname, uid=None, sshkeyfile=None):
    """ 
    This function retreives an AWS key/secret for uploading the live image. 
    """
    if uid is None:
        config=SSHConfig.from_path(os.path.expanduser('~/.ssh/config'))
        sitecfg = config.lookup(servername)
        if 'user' not in sitecfg.keys():
            log.warning(f'unable to connect to {servername} - no entry in ssh config file')
            return 
    else:
        sitecfg={}
        sitecfg['hostname'] = servername
        sitecfg['user'] = uid
        sitecfg['identityfile'] = [os.path.expanduser(sshkeyfile)]
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.RSAKey.from_private_key_file(sitecfg['identityfile'][0])
    key = ''
    try: 
        ssh_client.connect(sitecfg['hostname'], username=sitecfg['user'], pkey=pkey, look_for_keys=False)
        ftp_client = ssh_client.open_sftp()
        try:
            handle, tmpfnam = tempfile.mkstemp()
            ftp_client.get(remotekeyname + '.csv', tmpfnam)
        except Exception as e:
            log.error('unable to find AWS key')
            log.info(e, exc_info=True)
        ftp_client.close()
        try:
            lis = open(tmpfnam, 'r').readlines()
            os.close(handle)
            os.remove(tmpfnam)
            key, sec = lis[1].split(',')
        except Exception as e:
            log.error('malformed AWS key')
            log.info(e, exc_info=True)
    except Exception as e:
        log.error('unable to retrieve AWS key')
        log.info(e, exc_info=True)
    ssh_client.close()
    if key:
        log.info('retrieved key details')
        return key.strip(), sec.strip() 
    else: 
        return False, False


def pushLatestMonthlyStack(targetname, imgname):
    config=SSHConfig.from_path(os.path.expanduser('~/.ssh/config'))
    sitecfg = config.lookup(targetname)
    if 'user' not in sitecfg.keys():
        log.warning(f'unable to connect to {targetname} - no entry in ssh config file')
        return 
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.RSAKey.from_private_key_file(sitecfg['identityfile'][0])
    try:
        ssh_client.connect(sitecfg['hostname'], username=sitecfg['user'], pkey=pkey, look_for_keys=False)
        ftp_client = ssh_client.open_sftp()
        _, fname = os.path.split(imgname)
        camid = fname[:6]
        if os.path.isfile(imgname):
            ftp_client.put(imgname, f'data/meteors/{camid}_latest.jpg')
            log.info(f'uploaded {fname} to {targetname}')
        else:
            log.warning(f'file {imgname} not found')
    except Exception as e:
        log.warning(f'upload to {sitecfg["hostname"]}')
        log.info(e, exc_info=True)
    return 


def pushLatestDailyStack(config, arch_dir, localcfg, s3):
    stacklist = [f for f in glob.glob(os.path.join(arch_dir,'*_stack_*.jpg'))]
    if len(stacklist) ==0:
        return 
    imgname = stacklist[0]
    _, fname = os.path.split(imgname)
    tmpfname = os.path.join('/tmp', fname)
    if os.path.isfile(tmpfname):
        os.remove(tmpfname)
    shutil.copyfile(imgname, tmpfname)
    metcount = int(fname[fname.find('stack')+6:].split('_')[0]) - 1
    camid = config.stationID
    annotateImage(tmpfname, camid, metcount=metcount, rundate=fname[7:15])
    hn = localcfg['postprocess']['host']
    if hn[:3] == 's3:':
        log.info('uploading to {:s}/{:s}/{:s}'.format(hn, camid, 'dailystacks'))
        target=hn[5:]
        outf = '{:s}/dailystacks/{:s}'.format(camid, fname[:15]+'.jpg')
        try: 
            s3.meta.client.upload_file(tmpfname, target, outf, ExtraArgs ={'ContentType': 'image/jpg'})
        except Exception as e:
            log.warning('upload to S3 failed')
            log.info(e, exc_info=True)
        os.remove(tmpfname)
    else:
        log.info('target is not s3, not uploading daily stack')
    return 


def copyMLRejects(cap_dir, arch_dir, config):
    rej_dir = arch_dir.replace('ArchivedFiles','RejectedFiles')
    os.makedirs(rej_dir, exist_ok=True)
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
        trgfile = os.path.join(rej_dir, ff_file)
        if os.path.isfile(srcfile) and not os.path.isfile(trgfile):
            log.info(f'copying reject {os.path.basename(srcfile)} to {rej_dir}')
            shutil.copyfile(srcfile, trgfile)
    shutil.make_archive(rej_dir + '_rejected', 'zip', root_dir = rej_dir, base_dir=rej_dir)
    # housekeep the Rejects
    orig_count = 0
    final_count = 0
    base_dir, _ = os.path.split(rej_dir)
    if config.arch_dirs_to_keep > 0:
        archdir_list = getNightDirs(base_dir, config.stationID)
        orig_count = len(archdir_list)
        while len(archdir_list) > config.arch_dirs_to_keep:
            archdir_list = deleteNightFolders(base_dir, config)
        final_count = len(archdir_list)
    log.info('Purged {} older folders from RejectedFiles'.format(orig_count - final_count))
    orig_count = 0
    final_count = 0
    if config.bz2_files_to_keep > 0:
        bz2_list = glob.glob(f'{base_dir}/*.zip')
        orig_count = len(bz2_list)
        while len(bz2_list) > config.bz2_files_to_keep:
            os.remove(os.path.join(base_dir, bz2_list[0]))
            bz2_list.pop(0)
        final_count = len(bz2_list)
    log.info('Purged {} older zip files from RejectedFiles'.format(orig_count - final_count))
    return 


def monthlyStack(cfg, arch_dir, localcfg, s3):
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
        hn = localcfg['postprocess']['host']
        if hn[:3] == 's3:':
            log.info('uploading to {:s}/{:s}/{:s}'.format(hn, stn, 'stacks'))
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
        pushLatestMonthlyStack(webserver, targ)
    return     


def doTrackStack(arch_dir, cfg, localcfg, s3):
    trackStack([arch_dir], cfg, draw_constellations=True, hide_plot=True, background_compensation=False)
    tflist = glob.glob(os.path.join(arch_dir, '*_track_stack.jpg'))
    if len(tflist) > 0:
        trackfile = tflist[0]
        currdir = os.path.basename(os.path.normpath(arch_dir))
        lis = open(os.path.join(arch_dir, 'FTPdetectinfo_'+currdir+'.txt'), 'r').readlines()
        metcount = lis[0].split('=')[1].strip()
        currdir = os.path.basename(os.path.normpath(arch_dir))
        annotateImage(trackfile, cfg.stationID, int(metcount), currdir[7:15])
    else:
        log.info('no trackstack available today')
        sflist = glob.glob(os.path.join(arch_dir, '*_stack_*.jpg'))
        if len(sflist) ==0: 
            return 
        sfil = sflist[0]
        trackfile = sfil[:sfil.find('_stack_')] + '_track_stack.jpg'
        trackfile = os.path.join('/tmp', os.path.split(trackfile)[1])
        shutil.copyfile(sfil, trackfile)
        my_image = Image.open(trackfile)
        width, height = my_image.size
        image_editable = ImageDraw.Draw(my_image)
        fntheight=100
        try:
            fnt = ImageFont.truetype("arial.ttf", fntheight)
        except:
            fnt = ImageFont.truetype("DejaVuSans.ttf", fntheight)
        #fnt = ImageFont.load_default()
        image_editable.text((20,height/2), "NO TRACKSTACK TODAY", font=fnt, fill=(255))
        my_image.save(trackfile)

    hn = localcfg['postprocess']['host']
    if hn[:3] == 's3:':
        log.info('uploading to {:s}/{:s}/{:s}'.format(hn, cfg.stationID, 'trackstacks'))
        target=hn[5:]
        outf = f'{cfg.stationID}/trackstacks/{os.path.basename(trackfile)[:15]}.jpg'
        try: 
            s3.meta.client.upload_file(trackfile, target, outf, ExtraArgs ={'ContentType': 'image/jpg'})
        except Exception as e:
            log.warning('upload to S3 failed')
            log.info(e, exc_info=True)
    else:
        log.info('target is not s3, not uploading monthly stack')
    if len(tflist) == 0 and '/tmp' in trackfile:
        if os.path.isfile(trackfile):
            os.remove(trackfile)
    return 


def archiveBz2(config=None, localcfg=None):
    if localcfg is None:
        srcdir = os.path.split(os.path.abspath(__file__))[0]
        localcfg = configparser.ConfigParser()
        localcfg.read(os.path.join(srcdir, 'config.ini'))
    if config is None:
        rmscfg = os.path.expanduser('~/source/RMS/.config')
        config = cr.parse(rmscfg)
    sshconfig=SSHConfig.from_path(os.path.expanduser('~/.ssh/config'))
    camid = config.stationID.lower()
    datadir = config.data_dir
    sitecfg = sshconfig.lookup(localcfg['backup']['target'])  
    pkey = paramiko.RSAKey.from_private_key_file(sitecfg['identityfile'][0])  
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(sitecfg['hostname'], username=sitecfg['user'], pkey=pkey, look_for_keys=False)
        ftp = ssh_client.open_sftp()
        yr=0
        localbzs = glob.glob(f'{datadir}/ArchivedFiles/*.bz2')
        for locbz in localbzs:
            locbzfn = os.path.split(locbz)[1]
            if yr != locbz[7:11]:
                yr = locbzfn[7:11]
                rempath = f'{localcfg["backup"]["remotepath"]}/{camid}/{yr}'
                try:
                    rembzs = ftp.listdir(rempath)
                except Exception:
                    ftp.mkdir(rempath)
                    rembzs = []
            if locbzfn not in rembzs:
                remfnam = os.path.join(rempath, locbzfn)
                log.info(f'archiving {locbzfn}')
                ftp.put(locbz, remfnam)
        localbzs = glob.glob(f'{datadir}/RejectedFiles/*.zip')
        for locbz in localbzs:
            locbzfn = os.path.split(locbz)[1]
            if yr != locbz[7:11]:
                yr = locbzfn[7:11]
                rempath = f'{localcfg["backup"]["remotepath"]}/{camid}/{yr}'
                try:
                    rembzs = ftp.listdir(rempath)
                except Exception:
                    ftp.mkdir(rempath)
                    rembzs = []
            if locbzfn not in rembzs:
                remfnam = os.path.join(rempath, locbzfn)
                log.info(f'archiving {locbzfn}')
                ftp.put(locbz, remfnam)
        ftp.close()
    except Exception as e:
        log.warning(f"unable to archive the bz2 file to {sitecfg['hostname']}")
        log.warning(e, exc_info=True)


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

    mp4name = os.path.basename(cap_dir) + '_timelapse.mp4'
    if os.path.exists(os.path.join(srcdir, 'token.pickle')):
        # upload mp4 to youtube
        if not os.path.isfile(os.path.join(srcdir, '.ytdone')):
            with open(os.path.join(srcdir, '.ytdone'), 'w') as f:
                f.write('dummy\n')

        line = open(os.path.join(srcdir, '.ytdone'), 'r').readline().rstrip()
        if line != mp4name:
            tod = mp4name.split('_')[1]
            tod = tod[:4] +'-'+ tod[4:6] + '-' + tod[6:8]
            msg = '{:s} timelapse for {:s}'.format(hname, tod)
            log.info('uploading {:s} to youtube'.format(mp4name))
            for retries in range(0,5):
                try:
                    if stu.main(msg, os.path.join(arch_dir, mp4name)):
                        break
                except Exception as e:
                    log.info('problem with youtube upload, retrying in 10s')
                    log.debug(e, exc_info=True)
                    time.sleep(10)
                    retries -= 1
            if retries == 5:
                log.info('unable to upload timelapse after five retries')
        else:
            log.info('already uploaded {:s}'.format(mp4name))
                
        open(os.path.join(srcdir, '.ytdone'), 'w').write(mp4name)
    
    s3 = None
    if int(localcfg['postprocess']['upload']) == 1:
        # copy the ML rejected files
        copyMLRejects(cap_dir, arch_dir, config)

        # upload the MP4 to S3 or a website
        hn = localcfg['postprocess']['host']
        fn = os.path.join(arch_dir, mp4name)
        splits = mp4name.split('_')
        stn = splits[0]
        yymm = splits[1]
        yymm = yymm[:6]
        log.info('uploading to {:s}/{:s}/{:s}'.format(hn, stn, yymm))

        idfile = os.path.expanduser(localcfg['postprocess']['idfile'])
        idserver = localcfg['postprocess']['webserver']
        key, secret = getAWSKey(idserver, hname, hname, idfile)
        s3 = boto3.resource('s3', aws_access_key_id = key, aws_secret_access_key = secret, 
            region_name='eu-west-2')
        target=hn[5:]
        outf = '{:s}/{:s}/{:s}'.format(stn, yymm, mp4name[:15]+'_timelapse.mp4')
        try: 
            s3.meta.client.upload_file(fn, target, outf, ExtraArgs ={'ContentType': 'video/mp4'})
        except Exception as e:
            log.warning('upload to S3 failed')
            log.info(e, exc_info=True)

        # upload daily stack
        log.info('uploading daily stack')
        pushLatestDailyStack(config, arch_dir, localcfg, s3)

        # create monthly stack
        log.info('creating monthly stack')
        monthlyStack(config, arch_dir, localcfg, s3)
        # create trackstack
        log.info('creating trackstack')
        try: 
            doTrackStack(arch_dir, config, localcfg, s3)
        except Exception as e:
            log.warning('trackstack failed, probably too many detections')
            log.info(e, exc_info=True)
            sendAnEmail('markmcintyre99@googlemail.com',f'trackstack on {hname} failed',
                        'Warning',f'{hname}@themcintyres.ddns.net')

        archiveBz2(config, localcfg)

    if len(localcfg['mqtt']['broker']) > 1:
        log.info('sending to MQ')
        try:
            sendToMqtt(config)
        except Exception as e:
            log.warning('problem sending to MQTT')
            log.info(e, exc_info=True)

    os.remove(rebootlockfile)

    # clear log handlers again
    while len(log.handlers) > 0:
        log.removeHandler(log.handlers[0])
    return


if __name__ == '__main__':
    hname = os.uname()[1]
    if len(sys.argv) > 2: 
        rmscfg = os.path.expanduser(sys.argv[2])
    else:
        rmscfg = os.path.expanduser('~/source/RMS/.config')
    config = cr.parse(rmscfg)
    datadir = config.data_dir
    if len(sys.argv) < 2:
        lastcap = sorted(os.listdir(os.path.join(datadir, 'CapturedFiles')))[-1]
        if not os.path.isdir(os.path.join(datadir, 'ArchivedFiles', lastcap)): 
            lastcap = sorted(os.listdir(os.path.join(datadir, 'CapturedFiles')))[-2]
    else:
        lastcap = sys.argv[1]
    cap_dir = os.path.join(datadir, 'CapturedFiles', lastcap)
    arch_dir = os.path.join(datadir, 'ArchivedFiles', lastcap)
    print('processing {}'.format(lastcap))
    srcdir = os.path.split(os.path.abspath(__file__))[0]
    localcfg = configparser.ConfigParser()
    localcfg.read(os.path.join(srcdir, 'config.ini'))
    rmsExternal(cap_dir, arch_dir, config)
