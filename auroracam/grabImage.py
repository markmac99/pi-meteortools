# simple python programme to capture a jpg from an IP camera
import cv2
import sys
import os
import shutil
from RMS.CaptureDuration import captureDuration
import datetime 
import time 
import subprocess
from annotateImage import annotateImage
import boto3 
import logging 
import logging.handlers
from setExpo import setCameraExposure


pausetime = 2 # time to wait between capturing frames 
log = logging.getLogger("logger")


def getStartEndTimes(datadir):
    starttime, dur=captureDuration(51.88,-1.31,80) 
    if starttime is True:
        # we are starting after dusk so find out if there's already a folder
        # and use that instead
        log.info('after overnight start time')

        # if starttime=True, then dur is the number of seconds from now to end time.
        starttime = datetime.datetime.utcnow()
        endtime = starttime + datetime.timedelta(seconds=dur)
        # see if there's an existing folder for the data
        dirs=[]
        flist = os.listdir(datadir)
        for fl in flist:
            if os.path.isdir(os.path.join(datadir, fl)):
                dirs.append(fl)
        dirs.sort()
        laststart = datetime.datetime.strptime(dirs[-1], '%Y%m%d_%H%M%S')
        log.info(f'found folder {dirs[-1]}')

        # if its between noon and midnight on the same day, reuse the folder
        if starttime.hour > 12 and laststart.day == starttime.day:
            log.info(f'using {dirs[-1]}')
            starttime = laststart

        # if its between midnight and noon, and the dates are less than two full 
        # days apart, reuse the  folder. 
        elif starttime.hour <= 12 and (starttime - laststart).days < 2:
            log.info(f'using {dirs[-1]}')
            starttime = laststart
        else:
            pass
    else:
        # start time is in the future, so add on  dur seconds to get end time
        endtime = starttime + datetime.timedelta(seconds=dur)
    log.info(f'night starts at {starttime} and ends at {endtime}')
    return starttime, endtime


def grabImage(ipaddress, fnam, camid, now):
    capstr = f'rtsp://{ipaddress}:554/user=admin&password=&channel=1&stream=0.sdp'
    # log.info(capstr)
    try:
        cap = cv2.VideoCapture(capstr)
        ret, frame = cap.read()
        cap.release()
    except:
        log.info('unable to grab frame')
        return 
    x = 0
    while x < 5:
        try:
            cv2.imwrite(fnam, frame)
            x = 5
        except:
            x = x + 1
    cap.release()
    cv2.destroyAllWindows()
    title = f'{camid} {now.strftime("%Y-%m-%d %H:%M:%S")}'
    annotateImage(fnam, title, color='#FFFFFF')
    return 


def makeTimelapse(dirname, s3, camname):
    dirname = os.path.normpath(os.path.expanduser(dirname))
    _, mp4shortname = os.path.split(dirname)
    mp4name = os.path.join(dirname, mp4shortname + '.mp4')
    log.info(f'creating {mp4name}')
    fps = int(250/pausetime)
    if os.path.isfile(mp4name):
        os.remove(mp4name)
    cmdline = f'ffmpeg -v quiet -r {fps} -pattern_type glob -i "{dirname}/*.jpg" \
        -vcodec libx264 -pix_fmt yuv420p -crf 25 -movflags faststart -g 15 -vf "hqdn3d=4:3:6:4.5,lutyuv=y=gammaval(0.77)"  \
        {mp4name}'
    log.info(f'making timelapse of {dirname}')
    subprocess.call([cmdline], shell=True)
    log.info('done')
    targkey = f'{camname}/{mp4shortname[:6]}/{camname}_{mp4shortname}.mp4'
    try:
        s3.meta.client.upload_file(mp4name, 'mjmm-data', targkey, ExtraArgs = {'ContentType': 'video/mp4'})
    except:
        log.info('unable to upload mp4')
    return 


def setupLogging():
    print('about to initialise logger')
    logdir = os.getenv('LOGDIR', default=os.path.expanduser('~/RMS_data/logs'))
    os.makedirs(logdir, exist_ok=True)

    logfilename = os.path.join(logdir, 'auroracam_' + datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S.%f') + '.log')
    handler = logging.handlers.TimedRotatingFileHandler(logfilename, when='D', interval=1) 
    handler.setLevel(logging.INFO)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s-%(levelname)s-%(module)s-line:%(lineno)d - %(message)s', 
        datefmt='%Y/%m/%d %H:%M:%S')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s-%(levelname)s-%(module)s-line:%(lineno)d - %(message)s', 
        datefmt='%Y/%m/%d %H:%M:%S')
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.setLevel(logging.INFO)
    log.setLevel(logging.DEBUG)
    log.info('logging initialised')
    return 


if __name__ == '__main__':
    ipaddress = sys.argv[1]
    camid = sys.argv[2]
    if len(sys.argv)> 4:
        force_day = True
    else:
        force_day = False

    s3 = boto3.resource('s3')
    setupLogging()

    nightgain = int(os.getenv('NIGHTGAIN', default='70'))

    datadir = os.getenv('DATADIR', default=os.path.expanduser('~/RMS_data/auroracam'))
    os.makedirs(datadir, exist_ok=True)
    norebootflag = os.path.join(datadir, '..', '.noreboot')
    if os.path.isfile(norebootflag):
        os.remove(norebootflag)
    
    # get todays dusk and tomorrows dawn times
    dusk, dawn = getStartEndTimes(datadir)
    dirnam = os.path.join(datadir, dusk.strftime('%Y%m%d_%H%M%S'))
    os.makedirs(dirnam, exist_ok=True)

    now = datetime.datetime.utcnow()
    if now > dawn or now < dusk:
        isnight = False
        setCameraExposure(ipaddress, 'DAY', nightgain, True)
    else:
        isnight = True
        setCameraExposure(ipaddress, 'NIGHT', nightgain, True)

    log.info(f'now {now}, night start {dusk}, end {dawn}')
    uploadcounter = 0
    while True:
        now = datetime.datetime.utcnow()
        if now < dawn and now > dusk:
            isnight = True
            setCameraExposure(ipaddress, 'NIGHT', nightgain, True)
        # if force_day then save a dated file for the daytime 
        if force_day is True:
            fnam = os.path.join(dirnam, now.strftime('%Y%m%d_%H%M%S') + '.jpg')
            os.makedirs(dirnam, exist_ok=True)
            grabImage(ipaddress, fnam, camid, now)
            log.info(f'grabbed {fnam}')

        # if we are in the daytime period, just grab an image
        elif now > dawn or now < dusk:
            # grab the image
            fnam = os.path.expanduser(os.path.join('~/RMS_data', 'live.jpg'))
            grabImage(ipaddress, fnam, camid, now)
            log.info(f'grabbed {fnam}')
            if isnight is True:
                # make the mp4
                norebootflag = os.path.join(datadir, '..', '.noreboot')
                open(norebootflag, 'w')
                makeTimelapse(dirnam, s3, 'UK9999')
                # refresh the dusk/dawn times for tomorrow
                dusk, dawn = getStartEndTimes(datadir)
                dirnam = os.path.join(datadir, dusk.strftime('%Y%m%d_%H%M%S'))
                os.makedirs(dirnam, exist_ok=True)
                setCameraExposure(ipaddress, 'DAY', nightgain, True)
                log.info('switched to daytime mode, now rebooting')
                isnight = False
                os.remove(norebootflag)
                os.system('/usr/bin/sudo /usr/sbin/shutdown -r now')

        # otherwise its night time so save a dated file
        else:
            isnight = True
            dirnam = os.path.join(datadir, dusk.strftime('%Y%m%d_%H%M%S'))
            os.makedirs(dirnam, exist_ok=True)
            fnam = os.path.join(dirnam, now.strftime('%Y%m%d_%H%M%S') + '.jpg')
            grabImage(ipaddress, fnam, camid, now)
            log.info(f'grabbed {fnam}')
            fnam2 = os.path.expanduser(os.path.join('~/RMS_data', 'live.jpg'))
            if os.path.isfile(fnam):
                shutil.copy(fnam, fnam2)
                log.info('updated live copy')
            else:
                log.info(f'{fnam} missing')

        uploadcounter += pausetime
        testmode = int(os.getenv('TESTMODE', default=0))
        if uploadcounter > 9 and testmode == 0:
            log.info('uploading live image')
            if os.path.isfile(fnam):
                try:
                    s3.meta.client.upload_file(fnam, 'mjmm-data', f'{camid}/live.jpg', ExtraArgs = {'ContentType': 'image/jpeg'})
                except:
                    log.info('unable to upload live image')
                    pass
                uploadcounter = 0
            else:
                uploadcounter -= pausetime
        if testmode == 1:
            log.info(f'would have uploaded {fnam}')
        log.info(f'sleeping for {pausetime} seconds')
        time.sleep(pausetime)
