# SetExpo.py
# sets the exposure on the IPCamera using Python_DVRIP
# Copyright (C) Mark McIntyre
#
#
import sys
import os
import ephem
import configparser
import datetime
from time import sleep

# make use of RMS functionality
import Utils.CameraControl as cc

from crontab import CronTab
from tackleyUtils import getRMSConfig


def setCameraExposure(config, daynight, nightgain=None, nightColor=False, autoExp=False):
    
    cc.cameraControlV2(config, "SwitchMode", daynight)
    if nightgain is not None and daynight =='night':
        cc.cameraControlV2(config, 'SetParam', ['Camera', 'GainParam', 'Gain', f'{nightgain}'])
    if nightColor or autoExp:
        sleep(30)

    if nightColor:
        cc.cameraControlV2(config, 'SetParam', ['Camera','DayNightColor','1'])
    if autoExp:
        cc.cameraControlV2(config, 'SetParam', ['Camera','ExposureParam','LeastTime','100'])
        cc.cameraControlV2(config, "SetParam", ["Camera", "BroadTrends", "AutoGain", "1"])


def getNextRiseSet(cfg):
    obs = ephem.Observer()
    obs.lat = float(cfg.latitude) / 57.3 # convert to radians, close enough for this
    obs.lon = float(cfg.longitude) / 57.3
    obs.elev = float(cfg.elevation)
    obs.horizon = -9.0 / 57.3 # degrees below horizon for darkness

    sun = ephem.Sun()
    rise = obs.next_rising(sun).datetime()
    set = obs.next_setting(sun).datetime()
    return rise, set


def addCrontabEntries(cfg):
    local_path =os.path.dirname(os.path.abspath(__file__))
    rmslogdir = os.path.expanduser(os.path.join(cfg.data_dir, cfg.log_dir))
    camid = cfg.stationID

    rise, set = getNextRiseSet(cfg)
    rise = rise + datetime.timedelta(minutes=5)
    set = set + datetime.timedelta(minutes=-5)

    cron = CronTab(user=True)
    found = False
    iter=cron.find_command(f'setIPCamExpo.sh DAY {camid}')
    for i in iter:
        if i.is_enabled():
            found = True
            i.hour.on(rise.hour)
            i.minute.on(rise.minute)
    if found is False:
        job = cron.new(f'{local_path}/setIPCamExpo.sh DAY {camid} > {rmslogdir}/setday-{camid}.log 2>&1')
        job.hour.on(rise.hour)
        job.minute.on(rise.minute)
        cron.write()

    found = False
    iter=cron.find_command(f'setIPCamExpo.sh NIGHT {camid}')
    for i in iter:
        if i.is_enabled():
            found = True
            i.hour.on(set.hour)
            i.minute.on(set.minute)
    if found is False:
        job = cron.new(f'{local_path}/setIPCamExpo.sh NIGHT {camid} > {rmslogdir}/setnight-{camid}.log 2>&1')
        job.hour.on(set.hour)
        job.minute.on(set.minute)
        cron.write()
    cron.write()
    return 


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('usage: python SetExpo.py day/night camid optional_NIGHTGAIN optional_docolor')
        exit()
        
    daynight = sys.argv[1].lower()
    camid = sys.argv[2]

    srcdir = os.path.split(os.path.abspath(__file__))[0]
    localcfg = configparser.ConfigParser()
    localcfg.read(os.path.join(srcdir, 'config.ini'))

    cfg = getRMSConfig(camid, localcfg)

    if len(sys.argv) > 2:
        nightgain = int(sys.argv[3])
    else:
        nightgain = 60

    if len(sys.argv) > 4:
        nightColor = True
    else:
        nightColor = False
    setCameraExposure(cfg, daynight, nightgain, nightColor)
    addCrontabEntries(cfg)
