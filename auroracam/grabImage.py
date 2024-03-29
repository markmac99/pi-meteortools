# simple python programme to capture a jpg from an IP camera
# Copyright (C) Mark McIntyre
#
import cv2
import sys
import os
import shutil
import datetime 
import time 
import subprocess
import configparser
from meteortools.utils import annotateImageArbitrary, getNextRiseSet
import boto3 
import logging 
import logging.handlers
from setExpo import setCameraExposure
from crontab import CronTab
import paho.mqtt.client as mqtt
import platform 


pausetime = 2 # time to wait between capturing frames 
log = logging.getLogger("logger")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected success")
    else:
        print("Connected fail with code", rc)


def on_publish(client, userdata, result):
    #print('data published - {}'.format(result))
    return


def sendToMQTT(broker):
    if broker is None:
        broker = 'wxsatpi'
    hname = platform.uname().node
    client = mqtt.Client(hname)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(broker, 1883, 60)
    usage = shutil.disk_usage('.')
    diskspace = round(usage.used/usage.total*100.0,2)
    topic = f'meteorcams/{hname}/diskspace'
    ret = client.publish(topic, payload=diskspace, qos=0, retain=False)
    return ret


def roundTime(dt):
    if dt.microsecond > 500000:
        dt = dt + datetime.timedelta(seconds=1, microseconds = -dt.microsecond)
    else:
        dt = dt + datetime.timedelta(microseconds = -dt.microsecond)
    return dt


def getStartEndTimes(currdt, thiscfg):
    lat = thiscfg['auroracam']['lat']
    lon = thiscfg['auroracam']['lon']
    ele = thiscfg['auroracam']['alt']
    risetm, settm = getNextRiseSet(lat, lon, ele, fordate=currdt)
    lastdawn, lastdusk = getNextRiseSet(lat, lon, ele, fordate = currdt - datetime.timedelta(days=1))
    if risetm < settm:
        settm = lastdusk
    # capture from an hour before dusk to an hour after dawn - camera autoadjusts now
    nextrise = roundTime(risetm) + datetime.timedelta(minutes=60)
    nextset = roundTime(settm) - datetime.timedelta(minutes=60)
    lastrise = roundTime(lastdawn) + datetime.timedelta(minutes=60)
    log.info(f'night starts at {nextset} and ends at {nextrise}')
    return nextset, nextrise, lastrise


def adjustColour(fnam, red=1, green=1, blue=1, fnamnew=None):
    img = cv2.imread(fnam, flags=cv2.IMREAD_COLOR)
    img[:,:,2]=img[:,:,2] * red
    img[:,:,1]=img[:,:,1] * green
    img[:,:,0]=img[:,:,0] * blue
    if fnamnew is None:
        fnamnew = fnam
    cv2.imwrite(fnamnew, img)    


def grabImage(ipaddress, fnam, hostname, now, thiscfg):
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
    title = f'{hostname} {now.strftime("%Y-%m-%d %H:%M:%S")}'
    radj, gadj, badj = (thiscfg['auroracam']['rgbadj']).split(',')
    radj = float(radj)
    gadj = float(gadj)
    badj = float(badj)
    if radj < 0.99 or gadj < 0.99 or badj < 0.99:
        adjustColour(fnam, red=radj, green=gadj, blue=badj)
    annotateImageArbitrary(fnam, title, color='#FFFFFF')
    return 


def makeTimelapse(dirname, s3, camname, bucket, daytimelapse=False):
    dirname = os.path.normpath(os.path.expanduser(dirname))
    _, mp4shortname = os.path.split(dirname)[:15]
    if daytimelapse:
        mp4name = os.path.join(dirname, mp4shortname + '_day.mp4')
    else:
        mp4name = os.path.join(dirname, mp4shortname + '.mp4')
    log.info(f'creating {mp4name}')
    fps = int(125/pausetime)
    if os.path.isfile(mp4name):
        os.remove(mp4name)
    cmdline = f'ffmpeg -v quiet -r {fps} -pattern_type glob -i "{dirname}/*.jpg" \
        -vcodec libx264 -pix_fmt yuv420p -crf 25 -movflags faststart -g 15 -vf "hqdn3d=4:3:6:4.5,lutyuv=y=gammaval(0.77)"  \
        {mp4name}'
    log.info(f'making timelapse of {dirname}')
    subprocess.call([cmdline], shell=True)
    log.info('done')
    if s3 is not None:
        if daytimelapse:
            targkey = f'{camname}/{mp4shortname[:6]}/{camname}_{mp4shortname}_day.mp4'
        else:
            targkey = f'{camname}/{mp4shortname[:6]}/{camname}_{mp4shortname}.mp4'
        try:
            log.info(f'uploading to {bucket}/{targkey}')
            s3.meta.client.upload_file(mp4name, bucket, targkey, ExtraArgs = {'ContentType': 'video/mp4'})
        except:
            log.info('unable to upload mp4')
    else:
        print('created but not uploading mp4')
    return 


def setupLogging(thiscfg, prefix='auroracam_'):
    print('about to initialise logger')
    logdir = os.path.expanduser(thiscfg['auroracam']['logdir'])
    os.makedirs(logdir, exist_ok=True)

    logfilename = os.path.join(logdir, prefix + datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S.%f') + '.log')
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



def addCrontabEntry(local_path):
    cron = CronTab(user=True)
    #found = False
    iter=cron.find_command('uploadLiveJpg.sh')
    for i in iter:
        if i.is_enabled():
            #found = True
            cron.remove(i)
    #dtstr = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    job = cron.new(f'sleep 60 && {local_path}/uploadLiveJpg.sh') # > {logdir}/uploadLiveJpg-{dtstr}.log 2>&1')
    job.every_reboot()
    cron.write()


if __name__ == '__main__':
    ipaddress = sys.argv[1]
    hostname = sys.argv[2]

    thiscfg = configparser.ConfigParser()
    local_path =os.path.dirname(os.path.abspath(__file__))
    thiscfg.read(os.path.join(local_path, 'config.ini'))
    setupLogging(thiscfg)

    ulloc = thiscfg['auroracam']['uploadloc']
    if ulloc[:5] == 's3://':
        s3 = boto3.resource('s3')
        bucket = ulloc[5:]
    else:
        print('not uploading to AWS S3')
        s3 = None
        bucket = None
    addCrontabEntry(local_path)

    nightgain = int(thiscfg['auroracam']['nightgain'])
    camid = thiscfg['auroracam']['camid']
    datadir = os.path.expanduser(thiscfg['auroracam']['datadir'])
    os.makedirs(datadir, exist_ok=True)
    norebootflag = os.path.join(datadir, '..', '.noreboot')
    if os.path.isfile(norebootflag):
        os.remove(norebootflag)
    
    # get todays dusk and tomorrows dawn times
    now = datetime.datetime.utcnow()
    dusk, dawn, lastdawn = getStartEndTimes(now, thiscfg)
    daytimelapse = int(thiscfg['auroracam']['daytimelapse'])
    if now > dawn or now < dusk:
        isnight = False
        setCameraExposure(ipaddress, 'DAY', nightgain, True, True)
    else:
        isnight = True
        setCameraExposure(ipaddress, 'NIGHT', nightgain, True, True)

    log.info(f'now {now}, dusk {dusk}, dawn {dawn} last dawn {lastdawn}')
    uploadcounter = 0
    while True:
        now = datetime.datetime.utcnow()
        fnam = os.path.expanduser(os.path.join(datadir, '..', 'live.jpg'))
        thiscfg.read(os.path.join(local_path, 'config.ini'))
        grabImage(ipaddress, fnam, hostname, now, thiscfg)
        log.info(f'grabbed {fnam}')
        lastdusk = dusk
        dusk, dawn, lastdawn = getStartEndTimes(now, thiscfg)
        if isnight:
            capdirname = os.path.join(datadir, dusk.strftime('%Y%m%d_%H%M%S'))
        else:
            capdirname = os.path.join(datadir, lastdawn.strftime('%Y%m%d_%H%M%S'))
        
        if dusk != lastdusk and isnight:
            # its dawn
            capdirname = os.path.join(datadir, lastdusk.strftime('%Y%m%d_%H%M%S'))
            
        if daytimelapse or isnight: 
            os.makedirs(capdirname, exist_ok=True)
            fnam2 = os.path.join(capdirname, now.strftime('%Y%m%d_%H%M%S') + '.jpg')
            shutil.copyfile(fnam, fnam2)
            log.info(f'and copied to {capdirname}')
        # when we move from day to night, make the day timelapse then switch exposure and flag
        if now < dawn and now > dusk and isnight is False:
            if daytimelapse:
                # make the daytime mp4
                norebootflag = os.path.join(datadir, '..', '.noreboot')
                open(norebootflag, 'w')
                makeTimelapse(capdirname, s3, camid, bucket, daytimelapse)
                os.remove(norebootflag)
            isnight = True
            setCameraExposure(ipaddress, 'NIGHT', nightgain, True, True)
            capdirname = os.path.join(datadir, dusk.strftime('%Y%m%d_%H%M%S'))
            os.makedirs(capdirname, exist_ok=True)

        # when we move from night to day, make the night timelapse then switch exposure and flag and reboot
        if dusk != lastdusk and isnight:
            norebootflag = os.path.join(datadir, '..', '.noreboot')
            open(norebootflag, 'w')
            makeTimelapse(capdirname, s3, camid, bucket)
            log.info('switched to daytime mode, now rebooting')
            setCameraExposure(ipaddress, 'DAY', nightgain, True, True)
            os.remove(norebootflag)
            os.system('/usr/bin/sudo /usr/sbin/shutdown -r now')

        uploadcounter += pausetime
        testmode = int(os.getenv('TESTMODE', default=0))
        if uploadcounter > 9 and testmode == 0 and s3 is not None:
            log.info('uploading live image')
            if os.path.isfile(fnam):
                try:
                    s3.meta.client.upload_file(fnam, bucket, f'{hostname}/live.jpg', ExtraArgs = {'ContentType': 'image/jpeg'})
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
