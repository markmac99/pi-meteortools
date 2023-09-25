from meteortools.utils import getNextRiseSet
import datetime
import os
import glob
import shutil


def reorganize():
    basedir = '/home/mark/RMS_data/auroracam'
    srcdir = os.path.join(basedir, '20230709_201347')
    lat = 51.88
    lon = -1.31
    ele = 80
    imglist = glob.glob1(srcdir,'*.jpg')
    imglist.sort()
    for img in imglist:
        imgdt = datetime.datetime.strptime(img[:15], '%Y%m%d_%H%M%S')
        # adjust to allow for night capture window being one hour either side of dawn
        if imgdt.hour > 12 and imgdt.hour < 22:
            imgdt = imgdt + datetime.timedelta(minutes=60)
        if imgdt.hour < 12 and imgdt.hour > 2:
            imgdt = imgdt - datetime.timedelta(minutes=60)
        risetm, settm = getNextRiseSet(lat, lon, ele, fordate=imgdt+datetime.timedelta(days=-1))
        prisetime = risetm + datetime.timedelta(minutes=60)
        psettime = settm - datetime.timedelta(minutes=60)
        #risetm, settm = getNextRiseSet(lat, lon, ele, fordate=imgdt)
        #nrisetime = risetm + datetime.timedelta(minutes=60)
        #nsettime = settm - datetime.timedelta(minutes=60)
        if prisetime < psettime:   
            targdir = os.path.join(basedir, psettime.strftime("%Y%m%d_%H%M%S"))
        else:
            targdir = os.path.join(basedir, prisetime.strftime("%Y%m%d_%H%M%S"))
        if targdir != srcdir:
            print(f'imgdt {imgdt} targdir {targdir}') #, {prisetime}, {psettime}, {nrisetime}, {nsettime}')
            os.makedirs(targdir, exist_ok=True)
            shutil.move(os.path.join(srcdir, img), targdir)
