# 
# python script thats called when the nightly run completes to 
# upload to S3 or website. filename configurable in config file
#
# Copyright (C) Mark McIntyre


import os
import sys
import glob
import configparser
import logging
import logging.handlers
import time
import shutil
import datetime 
from dateutil.relativedelta import relativedelta
import paramiko
from paramiko.config import SSHConfig
from PIL import Image, ImageFont, ImageDraw
import boto3
import argparse


from Utils.StackFFs import stackFFs
from RMS.Routines import MaskImage
from RMS.DeleteOldObservations import getNightDirs, deleteNightFolders
from Utils.TrackStack import trackStack
import Utils.BatchFFtoImage as bff2i
import RMS.ConfigReader as cr


from tackleyUtils import getRMSConfig
from tackleyUtils import getAWSKey

try:
    sys.path.append(os.path.expanduser('~/source/rms_mqtt'))
    from sendToMQTT import sendToMqtt # noqa:E402 # type: ignore
    gotSTMQ = True
except Exception:
    gotSTMQ = False


sys.path.append(os.path.split(os.path.abspath(__file__))[0])
import sendToYoutube as stu # noqa:E402
from setExpo import addCrontabEntries as setExpoAddCron # noqa:E402

log = logging.getLogger('tackleyloger')
log.setLevel(logging.INFO)


def setupLogging(logpath, logprefix='tackley_'):
    print('about to initialise logger')

    logdir = os.path.expanduser(logpath)
    os.makedirs(logdir, exist_ok=True)
    print('removing any existing log handlers')
    for handler in log.handlers[:]:
        log.removeHandler(handler)

    logfilename = os.path.join(logdir, f"{logprefix}{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S.%f')}.log")
    handler = logging.handlers.TimedRotatingFileHandler(logfilename, when='D', interval=1) 
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s-%(levelname)s-%(module)s-line:%(lineno)d - %(message)s', 
        datefmt='%Y/%m/%d %H:%M:%S')
    handler.setFormatter(formatter)
    log.addHandler(handler)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.WARNING)
    formatter = logging.Formatter(fmt='%(asctime)s-%(levelname)s-%(module)s-line:%(lineno)d - %(message)s', 
        datefmt='%Y/%m/%d %H:%M:%S')
    ch.setFormatter(formatter)
    log.addHandler(ch)

    log.setLevel(logging.INFO)
    log.info('logging initialised')
    return 


def purgeOldLogs(cfg, logpref, days=30):
    reftime = time.time() - 86400*days
    log_dir = os.path.join(cfg.data_dir, cfg.log_dir)
    for logf in glob.glob(os.path.join(log_dir, logpref + '*.log*')):
        if os.path.getmtime(logf) < reftime:
            os.remove(logf)
    return 


def annotateImage(img_path, statid, metcount, rundate=None):
    """
    Annotate an image with the station ID and date in the bottom left and meteor count in the  
    bottom right  

    Arguments:  
        img_path:   [str] full path and filename of the image to be annotated  
        statid:     [str] station ID string to use  
        metcount:   [int] number of meteors in the image  

    
    Keyword Args:  
        rundate:    [str] rundate in 'YYYYMM' or 'YYYYMMDD' format. Default is today.   

    """
    if rundate is not None:
        if len(rundate) > 6:
            now = datetime.datetime.strptime(rundate, '%Y%m%d')
            title = '{} {}'.format(statid, now.strftime('%Y-%m-%d'))
        else:
            now = datetime.datetime.strptime(rundate, '%Y%m')
            title = '{} {}'.format(statid, now.strftime('%Y-%m'))
    else:
        now = datetime.datetime.now()
        title = '{} {}'.format(statid, now.strftime('%Y-%m-%d'))

    my_image = Image.open(img_path)
    width, height = my_image.size
    image_editable = ImageDraw.Draw(my_image)
    fntheight=30
    try:
        fnt = ImageFont.truetype("arial.ttf", fntheight)
    except:
        fnt = ImageFont.truetype("DejaVuSans.ttf", fntheight)
    #fnt = ImageFont.load_default()
    image_editable.text((15,height-fntheight-15), title, font=fnt, fill=(255))
    metmsg = 'meteors: {:04d}'.format(metcount)
    image_editable.text((width-7*fntheight-15,height-fntheight-15), metmsg, font=fnt, fill=(255))
    my_image.save(img_path)


def addCrontabs(statid=''):
    srcdir = os.path.split(os.path.abspath(__file__))[0]
    localcfg = configparser.ConfigParser()
    localcfg.read(os.path.join(srcdir, 'config.ini'))
    cfg = getRMSConfig(statid,localcfg)
    ipaddr = cfg.deviceID.split('/')[2].split(':')[0]
    setExpoAddCron(ipaddr, cfg)
    return 


def pushLatestMonthlyStack(targetname, imgname):
    sshconfig = SSHConfig.from_path(os.path.expanduser('~/.ssh/config'))
    sitecfg = sshconfig.lookup(targetname)
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
        hname = os.uname()[1]
        if 'test' in hname:
            camid = hname

        if os.path.isfile(imgname):
            ftp_client.put(imgname, f'data/meteors/{camid}_latest.jpg')
            log.info(f'uploaded {fname} to {targetname}')
        else:
            log.warning(f'file {imgname} not found')
    except Exception as e:
        log.warning(f'upload to {sitecfg["hostname"]}')
        log.info(e, exc_info=True)
    return 


def pushLatestDailyStack(cfg, arch_dir, localcfg, s3):
    stacklist = [f for f in glob.glob(os.path.join(arch_dir,'*_stack*_meteors.jpg'))]
    if len(stacklist) == 0:
        log.info('no daily stack today')
        stacklist = [f for f in glob.glob(os.path.join(arch_dir,'*_captured_stack.jpg'))]
    imgname = stacklist[0]
    _, fname = os.path.split(imgname)
    tmpfname = os.path.join('/tmp', fname)
    if os.path.isfile(tmpfname):
        os.remove(tmpfname)
    shutil.copyfile(imgname, tmpfname)
    if 'captured' in fname:
        metcount = 0
    else:
        metcount = int(fname[fname.find('stack')+6:].split('_')[0]) - 1
    hname = os.uname()[1]
    camid = cfg.stationID
    if 'test' in hname:
        camid = hname

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


def copyMLRejects(cap_dir, arch_dir, cfg):
    rej_dir = arch_dir.replace('ArchivedFiles','RejectedFiles')
    os.makedirs(rej_dir, exist_ok=True)
    ftplist = [f for f in glob.glob(os.path.join(arch_dir,'FTPdetectinfo*.txt')) if 'backup' not in f and 'uncalibrated' not in f]
    detlist = [f for f in ftplist if 'unfiltered' not in f]
    if len(detlist)==0: 
        return 
    if len(detlist)==0: 
        return 
    detlist = detlist[0]
    uflist = [f for f in ftplist if 'unfiltered' in f]
    if len(uflist) == 0:
        return 
    if len(uflist) == 0:
        return 
    uflist = uflist[0]
    
    dets = [li.strip() for li in open(detlist,'r').readlines() if 'FF_' in li]
    ufdets = [li.strip() for li in open(uflist,'r').readlines() if 'FF_' in li]
    rejs = [li for li in ufdets if li not in dets]
    if len(rejs) > 0:
        for ff_file in rejs:
            srcfile = os.path.join(cap_dir, ff_file)
            trgfile = os.path.join(rej_dir, ff_file)
            if os.path.isfile(srcfile) and not os.path.isfile(trgfile):
                log.info(f'copying reject {os.path.basename(srcfile)} to {rej_dir}')
                shutil.copyfile(srcfile, trgfile)
        shutil.make_archive(rej_dir + '_rejected', 'zip', root_dir = rej_dir, base_dir=rej_dir)
    log.info('housekeeping rejects')
    if len(rejs) > 0:
        for ff_file in rejs:
            srcfile = os.path.join(cap_dir, ff_file)
            trgfile = os.path.join(rej_dir, ff_file)
            if os.path.isfile(srcfile) and not os.path.isfile(trgfile):
                log.info(f'copying reject {os.path.basename(srcfile)} to {rej_dir}')
                shutil.copyfile(srcfile, trgfile)
        shutil.make_archive(rej_dir + '_rejected', 'zip', root_dir = rej_dir, base_dir=rej_dir)
    log.info('housekeeping rejects')
    orig_count = 0
    final_count = 0
    base_dir, _ = os.path.split(rej_dir)
    if cfg.arch_dirs_to_keep > 0:
        archdir_list = getNightDirs(base_dir, cfg.stationID)
        orig_count = len(archdir_list)
        while len(archdir_list) > cfg.arch_dirs_to_keep:
            archdir_list = deleteNightFolders(base_dir, cfg)
        final_count = len(archdir_list)
    log.info('Purged {} older folders from RejectedFiles'.format(orig_count - final_count))
    orig_count = 0
    final_count = 0
    if cfg.bz2_files_to_keep > 0:
        bz2_list = glob.glob(f'{base_dir}/*.zip')
        orig_count = len(bz2_list)
        while len(bz2_list) > cfg.bz2_files_to_keep:
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
    log.info(f'looking in {arch_dir}')
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
    log.info('stack created')
    jpgfiles = glob.glob(os.path.join(tmpdir, '*.jpg'))
    if len(jpgfiles) > 0:
        hname = os.uname()[1]
        stn = cfg.stationID
        print(f'{hname} {stn}')
        if 'test' in hname:
            stn = hname
        flist = glob.glob(os.path.join(tmpdir, '*.fits'))
        annotateImage(jpgfiles[0], stn, metcount=len(flist), rundate=currdir[7:13])
        targ = os.path.join(arch_dir, currdir[:13]+'.jpg')
        log.info(f'copying{jpgfiles[0]} to {targ}')
        shutil.copyfile(jpgfiles[0], targ)
        hn = localcfg['postprocess']['host']
        if hn[:3] == 's3:':
            log.info('uploading to {:s}/{:s}/{:s}'.format(hn, stn, 'stacks'))
            target=hn[5:]
            outf = '{:s}/stacks/{:s}'.format(stn, currdir[:13]+'.jpg')
            try: 
                s3.meta.client.upload_file(jpgfiles[0], target, outf, ExtraArgs ={'ContentType': 'image/jpg'})
            except Exception as e:
                log.warning('upload to S3 failed')
                log.info(e, exc_info=True)
        else:
            log.info('target is not s3, not uploading monthly stack')
        webserver = localcfg['postprocess']['webserver']
        pushLatestMonthlyStack(webserver, targ)
    else:
        log.warning('no stack created')
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
        hname = os.uname()[1]
        camid = cfg.stationID
        if 'test' in hname:
            camid = hname

        annotateImage(trackfile, camid, int(metcount), currdir[7:15])
    else:
        log.info('no trackstack available today')
        stackfile = os.path.join(arch_dir, '*_stack.jpg')
        sflist = glob.glob(stackfile)
        if len(sflist) == 0: 
            log.info('no stack file available either, using thumbs')
            sflist = glob.glob(os.path.join(arch_dir, '*_thumbs.jpg'))
        sfil = sflist[0]
        trackfile = os.path.split(sfil.replace('_stack.jpg','_track_stack.jpg'))[1]
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
    #log.info(f'trackstack is {trackfile}')

    hn = localcfg['postprocess']['host']
    if hn[:3] == 's3:':
        hname = os.uname()[1]
        camid = cfg.stationID
        if 'test' in hname:
            camid = hname
        log.info('uploading to {:s}/{:s}/{:s}'.format(hn, camid, 'trackstacks'))
        target=hn[5:]
        outf = f'{camid}/trackstacks/{os.path.basename(trackfile)[:15]}.jpg'
        outf = f'{camid}/trackstacks/{os.path.basename(trackfile)[:15]}.jpg'
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


def resendTrackStack(arch_dir, cfg):
def resendTrackStack(arch_dir, cfg):
    # to reannotate and resend the trackstack if the automated process fails
    hname = os.uname()[1]
    camid = cfg.stationID
    if 'test' not in hname:
        hname = camid 
    localcfg = configparser.ConfigParser()
    srcdir = os.path.split(os.path.abspath(__file__))[0]
    localcfg.read(os.path.join(srcdir, 'config.ini'))
    hn = localcfg['postprocess']['host']
    idfile = os.path.expanduser(localcfg['postprocess']['idfile'])
    idserver = localcfg['postprocess']['idserver']
    key, secret = getAWSKey(idserver, hname, hname, idfile)
    s3 = boto3.resource('s3', aws_access_key_id = key, aws_secret_access_key = secret, region_name='eu-west-2')
    target=hn[5:]
    tflist = glob.glob(os.path.join(arch_dir, '*_track_stack.jpg'))
    trackfile = tflist[0]
    currdir = os.path.basename(os.path.normpath(arch_dir))
    lis = open(os.path.join(arch_dir, 'FTPdetectinfo_'+currdir+'.txt'), 'r').readlines()
    metcount = lis[0].split('=')[1].strip()
    currdir = os.path.basename(os.path.normpath(arch_dir))
    camid = cfg.stationID
    if 'test' in hname:
        camid = hname
    annotateImage(trackfile, camid, int(metcount), currdir[7:15])
    outf = f'{camid}/trackstacks/{os.path.basename(trackfile)[:15]}.jpg'
    s3.meta.client.upload_file(trackfile, target, outf, ExtraArgs ={'ContentType': 'image/jpg'})
    return 


def getInterestingFiles_(capdir, dt1, dt2):
def getInterestingFiles_(capdir, dt1, dt2):
    # a function to get all fits files between two date/time ranges
 
 
    t1 = datetime.datetime.strptime(dt1, '%Y%m%d_%H%M%S').timestamp()
    t2 = datetime.datetime.strptime(dt2, '%Y%m%d_%H%M%S').timestamp()
    currdir = os.path.basename(os.path.normpath(capdir))
    tmp_folder = os.path.join('/tmp/', currdir)
    os.makedirs(tmp_folder)
    for ff in glob.glob(os.path.join(capdir, 'FF*.fits')):
        fftime = os.path.getmtime(ff)
        if fftime > t1 and fftime <=t2:
            shutil.copyfile(ff, os.path.join(tmp_folder, os.path.basename(ff)))
            
    bff2i.batchFFtoImage(tmp_folder, 'jpg', True)
    zipf = shutil.make_archive(tmp_folder, 'zip', root_dir = tmp_folder, base_dir=tmp_folder)


    localcfg = configparser.ConfigParser()
    srcdir = os.path.split(os.path.abspath(__file__))[0]
    localcfg.read(os.path.join(srcdir, 'config.ini'))
    sshconfig = SSHConfig.from_path(os.path.expanduser('~/.ssh/config'))
    sitecfg = sshconfig.lookup(localcfg['backup']['target'])  
    pkey = paramiko.RSAKey.from_private_key_file(sitecfg['identityfile'][0])  
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(sitecfg['hostname'], username=sitecfg['user'], pkey=pkey, look_for_keys=False)
    ftp = ssh_client.open_sftp()
   
    camid = os.path.split(capdir)[1].split('_')[0]
    rempath = f'{localcfg["backup"]["remotepath"]}/{camid.lower()}/{currdir[7:11]}/{currdir}_saved.zip'
    camid = os.path.split(capdir)[1].split('_')[0]
    rempath = f'{localcfg["backup"]["remotepath"]}/{camid.lower()}/{currdir[7:11]}/{currdir}_saved.zip'
    ftp.put(zipf, rempath)
    ftp.close()
    ssh_client.close()
    shutil.rmtree(tmp_folder)
    os.remove(zipf)
    return 


def archiveBz2(cfg, localcfg):
    sshconfig=SSHConfig.from_path(os.path.expanduser('~/.ssh/config'))
    camid = cfg.stationID.lower()
    hname = os.uname()[1]
    if 'test' in hname:
        camid = hname
    datadir = cfg.data_dir
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


def rmsExternal(cap_dir, arch_dir, cfg):
    rebootlockfile = os.path.join(cfg.data_dir, cfg.reboot_lock_file)
    with open(rebootlockfile, 'w') as f:
        f.write('1')

    setupLogging(os.path.join(cfg.data_dir, cfg.log_dir), f'tackley_log_{cfg.stationID}_')
    log.info('tackley external script started')

    cap_dir = os.path.normpath(cap_dir)
    arch_dir = os.path.normpath(arch_dir)
    log.info(f'processing {cap_dir}')

    cap_dir = os.path.normpath(cap_dir)
    arch_dir = os.path.normpath(arch_dir)
    log.info(f'processing {cap_dir}')

    log.info('reading local config')
    srcdir = os.path.split(os.path.abspath(__file__))[0]
    localcfg = configparser.ConfigParser()
    localcfg.read(os.path.join(srcdir, 'config.ini'))


    sys.path.append(srcdir)
    hname = os.uname()[1]
    if 'test' not in hname:
        hname = cfg.stationID

    mp4name = os.path.basename(cap_dir) + '_timelapse.mp4'
    if os.path.exists(os.path.join(srcdir, 'token.pickle')):
        # upload mp4 to youtube
        already_done = []
        if os.path.isfile(os.path.join(srcdir, '.ytdone')):
            already_done = open(os.path.join(srcdir, '.ytdone')).readlines()
            already_done = [x.strip() for x in already_done]
        if mp4name not in already_done:
        already_done = []
        if os.path.isfile(os.path.join(srcdir, '.ytdone')):
            already_done = open(os.path.join(srcdir, '.ytdone')).readlines()
            already_done = [x.strip() for x in already_done]
        if mp4name not in already_done:
            tod = mp4name.split('_')[1]
            tod = tod[:4] +'-'+ tod[4:6] + '-' + tod[6:8]
            msg = '{:s} timelapse for {:s}'.format(hname, tod)
            log.info('uploading {:s} to youtube'.format(mp4name))
            for retries in range(0,5):
                try:
                    if stu.main(msg, os.path.join(arch_dir, mp4name)):
                        # reload the done list in case its been updated by another process
                        already_done = open(os.path.join(srcdir, '.ytdone')).readlines()
                        already_done = [x.strip() for x in already_done]
                        already_done.append(mp4name)
                        already_done = list(set(already_done))
                        already_done.sort()
                        open(os.path.join(srcdir, '.ytdone'), 'w').writelines([x + '\n' for x in already_done])
                        # reload the done list in case its been updated by another process
                        already_done = open(os.path.join(srcdir, '.ytdone')).readlines()
                        already_done = [x.strip() for x in already_done]
                        already_done.append(mp4name)
                        already_done = list(set(already_done))
                        already_done.sort()
                        open(os.path.join(srcdir, '.ytdone'), 'w').writelines([x + '\n' for x in already_done])
                        break
                except Exception as e:
                    log.info('problem with youtube upload, retrying in 10s')
                    if retries == 4:
                        log.debug(e, exc_info=True)
                    time.sleep(10)
            if retries == 5:
                log.info('unable to upload timelapse after five retries')
        else:
            log.info('already uploaded {:s}'.format(mp4name))
                
    
    if localcfg['mqtt']['domq'] == '1' and gotSTMQ:
        log.info('sending to MQ')
        sendToMqtt(cfg.stationID)

    # clear out older logfiles
    purgeOldLogs(cfg, 'tackley_', days=30)
    
    s3 = None
    if int(localcfg['postprocess']['upload']) == 1:
        # copy the ML rejected files
        log.info('copying ML rejects')
        copyMLRejects(cap_dir, arch_dir, cfg)

        # upload the MP4 to S3 or a website
        hn = localcfg['postprocess']['host']
        fn = os.path.join(arch_dir, mp4name)
        splits = mp4name.split('_')
        stn = splits[0]
        yymm = splits[1]
        yymm = yymm[:6]
        log.info('uploading to {:s}/{:s}/{:s}'.format(hn, stn, yymm))

        idfile = os.path.expanduser(localcfg['postprocess']['idfile']) + f'_{hname}'
        idserver = localcfg['postprocess']['idserver']
        # print(idfile, idserver)
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
        pushLatestDailyStack(cfg, arch_dir, localcfg, s3)

        # create monthly stack
        log.info('creating monthly stack')
        monthlyStack(cfg, arch_dir, localcfg, s3)
        # archive data to my server
        log.info('backing up the ArchivedFiles data')
        archiveBz2(cfg, localcfg)
        # create trackstack
        log.info('creating trackstack')
        try: 
            doTrackStack(arch_dir, cfg, localcfg, s3)
        except Exception as e:
            log.warning('trackstack failed, probably too many detections')
            log.info(e, exc_info=True)

    os.remove(rebootlockfile)
    log.info('done')
    # clear log handlers again
    while len(log.handlers) > 0:
        log.removeHandler(log.handlers[0])
    return


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="Run tackley postprocessing script.")
    arg_parser.add_argument('-d', '--dir_path', nargs=1, metavar='DIR_PATH', type=str,
        help='Path to CapturedFiles folder to process. Defaults to latest.')

    arg_parser.add_argument( '-c', '--config', nargs=1, metavar='CONFIG_PATH', type=str,
        help="Path to the RMS config file. Defaults to working it out from dir_path")
    
    arg_parser.add_argument( '-t', '--toolcfg', nargs=1, metavar='TOOL_CFG_PATH', type=str,
        help="Path to the tackley config file. Defaults to current directory.")
    
    cml_args = arg_parser.parse_args()

    if not cml_args.config and not cml_args.dir_path:
        print('Must supply either --dir_path or --config parameters or both')
        exit(1)

    if cml_args.config:
        cfg = cr.loadConfigFromDirectory(cml_args.config, 'notused')
    else:
        cfg = None # we will try to load it later

    localcfg = configparser.ConfigParser()
    if cml_args.toolcfg:
        localcfg.read(cml_args.toolcfg[0])
    else:
        # read from code source folder
        srcdir = os.path.split(os.path.abspath(__file__))[0]
        localcfg.read(os.path.join(srcdir, 'config.ini'))

    if cml_args.dir_path:
        lastcap = os.path.normpath(os.path.expanduser(cml_args.dir_path[0]))
        if not os.path.isdir(lastcap):
            print(f'Capture folder {cml_args.dir_path[0]} not found')
            exit(1)
    else:
        capdir = os.path.expanduser(os.path.join(cfg.data_dir, 'CapturedFiles'))
        recentcaps = os.listdir(capdir)
        recentcaps.sort()
        if len(recentcaps) >0:
            lastcap = recentcaps[-1]
        else:
            print(f'no captured data in {capdir}')
            exit(0)
    lastcap = os.path.split(lastcap)[1]
    if not cfg:
        camid = lastcap.split('_')[0]
        cfg = getRMSConfig(camid, localcfg)

    datadir = cfg.data_dir
    cap_dir = os.path.join(datadir, 'CapturedFiles', lastcap)
    arch_dir = os.path.join(datadir, 'ArchivedFiles', lastcap)
    print(f'processing {lastcap}')
    rmsExternal(cap_dir, arch_dir, cfg)
