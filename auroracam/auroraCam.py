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
import boto3 
import logging 
import logging.handlers
from setExpo import setCameraExposure
from crontab import CronTab
import paho.mqtt.client as mqtt
import platform 
import paramiko
import tempfile
from sendToYoutube import sendToYoutube
from makeImageIndex import createLatestIndex
from PIL import Image, ImageFont, ImageDraw 
import ephem


pausetime = 2 # time to wait between capturing frames 
log = logging.getLogger("logger")


def annotateImageArbitrary(img_path, message, color='#000'):
    """
    Annotate an image with an arbitrary message in the selected colour at the bottom left  

    Arguments:  
        img_path:   [str] full path and filename of the image to be annotated  
        message:    [str] message to put on the image  
        color:      [str] hex colour string, default '#000' which is black  

    """
    my_image = Image.open(img_path)
    width, height = my_image.size
    image_editable = ImageDraw.Draw(my_image)
    fntheight=30
    try:
        fnt = ImageFont.truetype("arial.ttf", fntheight)
    except Exception:
        fnt = ImageFont.truetype("DejaVuSans.ttf", fntheight)
    #fnt = ImageFont.load_default()
    image_editable.text((15,height-fntheight-15), message, font=fnt, fill=color)
    my_image.save(img_path)


def getNextRiseSet(lati, longi, elev, fordate=None):
    """ Calculate the next rise and set times for a given lat, long, elev  

    Paramters:  
        lati:   [float] latitude in degrees  
        longi:  [float] longitude in degrees (+E)  
        elev:   [float] latitude in metres  
        fordate:[datetime] date to calculate for, today if none

    Returns:  
        rise, set:  [date tuple] next rise and set as datetimes  

    Note that set may be earlier than rise, if you're invoking the function during daytime.  

    """
    obs = ephem.Observer()
    obs.lat = float(lati) / 57.3 # convert to radians, close enough for this
    obs.lon = float(longi) / 57.3
    obs.elev = float(elev)
    obs.horizon = -6.0 / 57.3 # degrees below horizon for darkness
    if fordate is not None:
        obs.date = fordate

    sun = ephem.Sun()
    rise = obs.next_rising(sun).datetime()
    set = obs.next_setting(sun).datetime()
    return rise, set


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected success")
    else:
        print("Connected fail with code", rc)


def on_publish(client, userdata, result):
    #print('data published - {}'.format(result))
    return


def sendToMQTT(broker=None):
    if broker is None:
        srcdir = os.path.split(os.path.abspath(__file__))[0]
        localcfg = configparser.ConfigParser()
        localcfg.read(os.path.join(srcdir, 'mqtt.cfg'))
    broker = localcfg['mqtt']['broker']
    hname = platform.uname().node
    client = mqtt.Client(hname)
    client.on_connect = on_connect
    client.on_publish = on_publish
    if localcfg['mqtt']['username'] != '':
        client.username_pw_set(localcfg['mqtt']['username'], localcfg['mqtt']['password'])
    if localcfg['mqtt']['username'] != '':
        client.username_pw_set(localcfg['mqtt']['username'], localcfg['mqtt']['password'])
    client.connect(broker, 1883, 60)
    usage = shutil.disk_usage('.')
    diskspace = round(usage.used/usage.total*100.0, 2)
    topicroot = localcfg['mqtt']['topic']
    topic = f'{topicroot}/{hname}/diskspace'
    ret = client.publish(topic, payload=diskspace, qos=0, retain=False)
    time.sleep(10)
    cpuf = '/sys/class/thermal/thermal_zone0/temp'
    cputemp = int(open(cpuf).readline().strip())/1000
    topic = f'{topicroot}/{hname}/cputemp'
    ret = client.publish(topic, payload=cputemp, qos=0, retain=False)
    return ret


def roundTime(dt):
    if dt.microsecond > 500000:
        dt = dt + datetime.timedelta(seconds=1, microseconds = -dt.microsecond)
    else:
        dt = dt + datetime.timedelta(microseconds = -dt.microsecond)
    return dt


def getAWSConn(thiscfg, remotekeyname, uid):
    """ 
    This function retreives an AWS key/secret for uploading the live image. 
    """
    servername = thiscfg['uploads']['idserver']
    if servername == '':
        # look for a local key file
        awskeyfile = thiscfg['uploads']['idkey']
        lis = open(os.path.expanduser(awskeyfile), 'r').readlines()
        keyline = lis[1].split(',')
        key = keyline[-2]
        sec = keyline[-1]
        pass
    else:
        # retrieve a keyfile from the server
        sshkeyfile = thiscfg['uploads']['idkey']
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file(os.path.expanduser(sshkeyfile))
        key = ''
        try: 
            ssh_client.connect(servername, username=uid, pkey=pkey, look_for_keys=False)
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
    s3 = None
    if key:
        log.info('retrieved key details')
        try:
            conn = boto3.Session(aws_access_key_id=key.strip(), aws_secret_access_key=sec.strip())
            s3 = conn.resource('s3')
            log.info('obtained s3 resource')
        except Exception as e:
            log.info(e, exc_info=True)
            pass
    if s3 is None:
        log.warning('no AWS key retrieved, trying current AWS profile')
        s3 = boto3.resource('s3')
    return s3


def getStartEndTimes(currdt, thiscfg, origdusk=None):
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
    # allow for small variations in dusk timing
    if origdusk:
        if (nextset - origdusk) < datetime.timedelta(seconds=10):
            nextset = origdusk
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
    except Exception as e:
        log.info('unable to grab frame')
        log.info(e, exc_info=True)
        return 
    x = 0
    done = False
    while x < 5:
        try:
            cv2.imwrite(fnam, frame)
            done = True
            break
        except Exception as e:
            log.info(f'unable to save image {fnam}')
            x = x + 1
            log.info(e, exc_info=True)
    cap.release()
    cv2.destroyAllWindows()
    if done:
        title = f'{hostname} {now.strftime("%Y-%m-%d %H:%M:%S")}'
        radj, gadj, badj = (thiscfg['auroracam']['rgbadj']).split(',')
        radj = float(radj)
        gadj = float(gadj)
        badj = float(badj)
        if radj < 0.99 or gadj < 0.99 or badj < 0.99:
            adjustColour(fnam, red=radj, green=gadj, blue=badj)
        annotateImageArbitrary(fnam, title, color='#FFFFFF')
    else:
        log.warning('no new image so not annotated')
    return 


def makeTimelapse(dirname, s3, camname, bucket, daytimelapse=False, maketimelapse=True, youtube=True):
    dirname = os.path.normpath(os.path.expanduser(dirname))
    _, mp4shortname = os.path.split(dirname)[:15]
    if daytimelapse:
        mp4name = os.path.join(dirname, mp4shortname + '_day.mp4')
    else:
        mp4name = os.path.join(dirname, mp4shortname + '.mp4')
    log.info(f'creating {mp4name}')
    fps = int(125/pausetime)
    if maketimelapse:
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
        except Exception as e:
            log.info('unable to upload mp4')
            log.info(e, exc_info=True)
    else:
        print('created but not uploading mp4 to s3')
    # upload night video to youtube
    if not daytimelapse and youtube is True:
        try:
            log.info('uploading to youtube')
            dtstr = mp4shortname[:4] + '-' + mp4shortname[4:6] + '-' + mp4shortname[6:8]
            title = f'Auroracam timelapse for {dtstr}'
            sendToYoutube(title, mp4name)
        except Exception as e:
            log.info('unable to upload mp4 to youtube')
            log.info(e, exc_info=True)
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


def uploadOneFile(fnam, ulloc, ftpserver, userid, sshkey):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.RSAKey.from_private_key_file(os.path.expanduser(sshkey))
    try: 
        targloc = os.path.join(ulloc, os.path.basename(fnam))
        ssh_client.connect(ftpserver, userid, pkey=pkey, look_for_keys=False)
        ftp_client = ssh_client.open_sftp()
        ftp_client.put(fnam, targloc)
        ftp_client.close()
        ssh_client.close()
    except Exception as e:
        log.warn(f'unable to upload to {ftpserver}:{targloc}')
        log.info(e, exc_info=True)
    return 


def addCrontabEntry(local_path):
    cron = CronTab(user=True)
    #found = False
    iter=cron.find_command('startAuroraCam.sh')
    for i in iter:
        if i.is_enabled():
            #found = True
            cron.remove(i)
    job = cron.new(f'sleep 60 && {local_path}/startAuroraCam.sh > /tmp/startup.log 2>&1')
    job.every_reboot()
    cron.write()
    iter=cron.find_command('archiveData.sh')
    for i in iter:
        if i.is_enabled():
            #found = True
            cron.remove(i)
    job = cron.new(f'0 12 * * * {local_path}/archiveData.sh > /dev/null 2>&1')
    cron.write()


if __name__ == '__main__':
    ipaddress = sys.argv[1]
    hostname = platform.uname().node
    hostname = platform.uname().node

    thiscfg = configparser.ConfigParser()
    local_path =os.path.dirname(os.path.abspath(__file__))
    thiscfg.read(os.path.join(local_path, 'config.ini'))
    setupLogging(thiscfg)

    s3 = None
    bucket = None
    ftpserver = None
    userid = None
    sshkey = None
    s3loc = thiscfg['uploads']['s3uploadloc']
    if s3loc != '':
        log.info(f'S3 upload target {s3loc}')
        # try to retrieve an AWS key from the sftp server
        s3 = getAWSConn(thiscfg, hostname, hostname)
        bucket = s3loc[5:]
    else:
        s3loc = None
        log.info('not uploading to S3')

    ftpserver = thiscfg['uploads']['ftpserver']
    if ftpserver != '':
        log.info(f'SFTP upload target {ftpserver}')
        userid = thiscfg['uploads']['ftpuser']
        sshkey = thiscfg['uploads']['ftpkey']
        ftploc = thiscfg['uploads']['ftpuploadloc']
    else:
        ftpserver = None
        log.info('not uploading to ftpserver')

    yt = False
    try: 
        if int(thiscfg['youtube']['doupload']) == 1:
            yt = True
    except Exception:
        log.info('not sending to youtube')

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
        dusk, dawn, lastdawn = getStartEndTimes(now, thiscfg, lastdusk)
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
            createLatestIndex(capdirname)
            log.info(f'and copied to {capdirname}')
        # when we move from day to night, make the day timelapse then switch exposure and flag
        if now < dawn and now > dusk and isnight is False:
            if daytimelapse:
                # make the daytime mp4
                norebootflag = os.path.join(datadir, '..', '.noreboot')
                open(norebootflag, 'w')
                makeTimelapse(capdirname, s3, camid, bucket, daytimelapse=True, youtube=yt)
                createLatestIndex(capdirname)
                os.remove(norebootflag)
            isnight = True
            setCameraExposure(ipaddress, 'NIGHT', nightgain, True, True)
            capdirname = os.path.join(datadir, dusk.strftime('%Y%m%d_%H%M%S'))
            os.makedirs(capdirname, exist_ok=True)

        # when we move from night to day, make the night timelapse then switch exposure and flag and reboot
        if dusk != lastdusk and isnight:
            norebootflag = os.path.join(datadir, '..', '.noreboot')
            open(norebootflag, 'w')
            makeTimelapse(capdirname, s3, camid, bucket, youtube=yt)
            createLatestIndex(capdirname)
            log.info('switched to daytime mode, now rebooting')
            setCameraExposure(ipaddress, 'DAY', nightgain, True, True)
            os.remove(norebootflag)
            try:
                os.system('/usr/bin/sudo /usr/sbin/shutdown -r now')
            except Exception as e:
                log.info('unable to reboot')
                log.info(e, exc_info=True)

        uploadcounter += pausetime
        testmode = int(os.getenv('TESTMODE', default=0))
        if uploadcounter > 9 and testmode == 0 and os.path.isfile(fnam):
            if s3 is not None:
                try:
                    s3.meta.client.upload_file(fnam, bucket, f'{hostname}/live.jpg', ExtraArgs = {'ContentType': 'image/jpeg'})
                    log.info(f'uploaded live image to {bucket}')
                except Exception as e:
                    log.warning(f'upload to {bucket} failed')
                    log.info(e, exc_info=True)
            if ftpserver is not None:
                try:
                    uploadOneFile(fnam, ftploc, ftpserver, userid, sshkey)
                    log.info(f'uploaded live image to {ftpserver}')
                except Exception as e:
                    log.warning(f'upload to {ftpserver} failed')
                    log.info(e, exc_info=True)
            uploadcounter = 0
        else:
            uploadcounter -= pausetime
        if testmode == 1:
            log.info(f'would have uploaded {fnam}')
        log.info(f'sleeping for {pausetime} seconds')
        time.sleep(pausetime)
