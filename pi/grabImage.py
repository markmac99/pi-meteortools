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


pausetime = 2 # time to wait between capturing frames 
log = logging.getLogger("logger")


def getStartEndTimes():
    starttime, dur=captureDuration(51.88,-1.31,80) 
    if starttime is True:
        # the batch took too long to run so just set starttime to now
        log.info(f'after overnight start time, {dur}')
        starttime = datetime.datetime.now()
    endtime = starttime + datetime.timedelta(seconds=dur)
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
    srcdir = os.path.dirname(os.path.abspath(__file__))
    print('about to initialise logger')
    with open(os.path.join(srcdir, 'config.ini'),'r') as inf:
        for li in inf.readlines():
            if 'LOGDIR' in li:
                logdir = li.split('=')[1].strip()
            if 'DATADIR' in li:
                datadir = li.split('=')[1].strip()
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
    return datadir


if __name__ == '__main__':
    ipaddress = sys.argv[1]
    camid = sys.argv[2]
    if len(sys.argv)> 4:
        force_day = True
    else:
        force_day = False

    s3 = boto3.resource('s3')
    datadir = setupLogging()
    os.makedirs(datadir, exist_ok=True)

    # get todays dusk and tomorrows dawn times
    dusk, dawn = getStartEndTimes()
    dirnam = os.path.join(datadir, camid, dusk.strftime('%Y%m%d_%H%M%S'))
    os.makedirs(dirnam, exist_ok=True)

    now = datetime.datetime.now()
    if now > dawn or now < dusk:
        isnight = False
    else:
        isnight = True

    log.info(f'now {now}, night start {dusk}, end {dawn}')
    uploadcounter = 0
    while True:
        now = datetime.datetime.now()
        if now < dawn and now > dusk:
            isnight = True
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
                makeTimelapse(dirnam, s3, 'UK9999')
                # refresh the dusk/dawn times for tomorrow
                dusk, dawn = getStartEndTimes()
                dirnam = os.path.join(datadir, camid, dusk.strftime('%Y%m%d_%H%M%S'))
                os.makedirs(dirnam, exist_ok=True)
                log.info('switched to daytime mode, now rebooting')
                isnight = False
                os.system('/usr/bin/sudo /usr/sbin/shutdown -r now')

        # otherwise its night time so save a dated file
        else:
            isnight = True
            dirnam = os.path.join(datadir, camid, dusk.strftime('%Y%m%d_%H%M%S'))
            os.makedirs(dirnam, exist_ok=True)
            fnam = os.path.join(dirnam, now.strftime('%Y%m%d_%H%M%S') + '.jpg')
            grabImage(ipaddress, fnam, camid, now)
            log.info(f'grabbed {fnam}')
            fnam2 = os.path.expanduser(os.path.join('~/RMS_data', 'live.jpg'))
            shutil.copy(fnam, fnam2)
            log.info('updated live copy')

        uploadcounter += pausetime
        if uploadcounter > 9:
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
        log.info(f'sleeping for {pausetime} seconds')
        time.sleep(pausetime)
