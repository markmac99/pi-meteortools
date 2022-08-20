# simple python programme to capture a jpg from an IP camera
import cv2
import sys
import os
from RMS.CaptureDuration import captureDuration
import datetime 
import time 
import subprocess
from annotateImage import annotateImage
import boto3 


def getStartEndTimes():
    starttime, dur=captureDuration(51.88,-1.31,80) 
    if starttime is True:
        # the batch took too long to run so just quit
        exit(0)

    endtime = starttime + datetime.timedelta(seconds=dur)
    return starttime, endtime


def grabImage(ipaddress, fnam, camid, now):
    capstr = f'rtsp://{ipaddress}:554/user=admin&password=&channel=1&stream=0.sdp'
    # print(capstr)
    cap = cv2.VideoCapture(capstr)
    ret, frame = cap.read()
    cv2.imwrite(fnam, frame)
    cap.release()
    cv2.destroyAllWindows()
    title = f'{camid} {now.strftime("%Y-%m-%d %H:%M:%S")}'
    annotateImage(fnam, title, color='#FFFFFF')
    return 


def makeTimelapse(dirnam, s3, camname):
    dirnam = os.path.normpath(os.path.expanduser(dirnam))
    _, mp4shortname = os.path.split(dirnam)
    mp4name = os.path.join(dirnam, mp4shortname + '.mp4')
    if os.path.isfile(mp4name):
        os.remove(mp4name)
    cmdline = f'ffmpeg -v quiet -r 25 -pattern_type glob -i "{dirnam}/*.jpg"  {mp4name}'
    print(f'making timelapse of {dirnam}')
    print(cmdline)
    subprocess.call([cmdline], shell=True)
    targkey = f'{camname}/{mp4shortname[:6]}/{camname}_{mp4shortname}.mp4'
    s3.meta.client.upload_file(mp4name, 'mjmm-data', targkey, ExtraArgs = {'ContentType': 'video/mp4'})
    return 


if __name__ == '__main__':
    ipaddress = sys.argv[1]
    dirnam = sys.argv[2]
    camid = sys.argv[3]
    if len(sys.argv)> 4:
        force_day = True
    else:
        force_day = False

    s3 = boto3.resource('s3')

    os.makedirs(dirnam, exist_ok=True)

    st, et = getStartEndTimes()
    now = datetime.datetime.now()
    dateddirnam = st.strftime('%Y%m%d_%H%M%S')
    dirnam = os.path.join(dirnam, camid, dateddirnam)
    os.makedirs(dirnam, exist_ok=True)

    if now > et or now < st:
        isnight = False
    else:
        isnight = True

    while True:
        now = datetime.datetime.now()
        # if force_day then save a dated file for the daytime 
        if force_day is True:
            fnam = os.path.join(dirnam, now.strftime('%Y%m%d_%H%M%S') + '.jpg')
            grabImage(ipaddress, fnam, camid, now)
            print(f'grabbed {fnam}')

        # if we are in the daytime period, just grab an image
        elif now > et or now < st:
            fnam = os.path.expanduser(os.path.join('~/RMS_data', 'live.jpg'))
            grabImage(ipaddress, fnam, camid, now)
            if isnight is True:
                makeTimelapse(dateddirnam, s3, 'UK9999')
                isnight = False
            print(f'grabbed {fnam}')

        # otherwise its night time so save a dated file
        else:
            isnight = True
            fnam = os.path.join(dirnam, now.strftime('%Y%m%d_%H%M%S') + '.jpg')
            grabImage(ipaddress, fnam, camid, now)
            print(f'grabbed {fnam}')
        
        s3.meta.client.upload_file(fnam, 'mjmm-data', f'{camid}/live.jpg', ExtraArgs = {'ContentType': 'image/jpeg'})
        time.sleep(10)
