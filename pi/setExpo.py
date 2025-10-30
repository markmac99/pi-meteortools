# SetExpo.py
# sets the exposure on the IPCamera using Python_DVRIP
# Copyright (C) Mark McIntyre
#
#
import os
import ephem
import configparser
import datetime
from time import sleep
import argparse

# make use of RMS functionality
import Utils.CameraControl as cc

from crontab import CronTab
from tackleyUtils import getRMSConfig


def setCameraExposure(config, daynight, nightgain=None, nightColor=False, autoExp=False, testmode=False):
    if testmode:
        print(f'would have switched {config.stationID} to {daynight} with gain {nightgain} color {nightColor} autoexp {autoExp}')
        return 
    if daynight == 'reboot':
        # determine what time it is and whether to switch to day or night mode
        daynight = getRequiredMode(config)
        
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


def getRequiredMode(cfg):
    now = datetime.datetime.now()
    rise, set = getNextRiseSet(cfg)
    rise = rise + datetime.timedelta(minutes=5)
    set = set + datetime.timedelta(minutes=-5)
    mode = 'day'
    if now > set or now < rise:
        mode = 'night'
    print(f'day-night mode is {mode}')
    return mode


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


def addCrontabEntries(cfg, testmode=False):
    local_path =os.path.dirname(os.path.abspath(__file__))
    if cfg.stationID in cfg.data_dir:
        root_data_dir = os.path.normpath(os.path.join(cfg.data_dir,'..'))
    else:
        root_data_dir = cfg.data_dir
    rmslogdir = os.path.expanduser(os.path.join(root_data_dir, cfg.log_dir))

    rise, set = getNextRiseSet(cfg)
    rise = rise + datetime.timedelta(minutes=5)
    set = set + datetime.timedelta(minutes=-5)

    if testmode:
        print(f'would have set crontabs for {rise} or {set}')
        return 
    cron = CronTab(user=True)
    found = False
    iter=cron.find_command('setIPCamExpo.sh DAY')
    for i in iter:
        if i.is_enabled():
            found = True
            i.hour.on(rise.hour)
            i.minute.on(rise.minute)
    if found is False:
        job = cron.new(f'{local_path}/setIPCamExpo.sh DAY > {rmslogdir}/setday.log 2>&1')
        job.hour.on(rise.hour)
        job.minute.on(rise.minute)
        cron.write()

    found = False
    iter=cron.find_command('setIPCamExpo.sh NIGHT')
    for i in iter:
        if i.is_enabled():
            found = True
            i.hour.on(set.hour)
            i.minute.on(set.minute)
    if found is False:
        job = cron.new(f'{local_path}/setIPCamExpo.sh NIGHT > {rmslogdir}/setnight.log 2>&1')
        job.hour.on(set.hour)
        job.minute.on(set.minute)
        cron.write()

    found = False
    iter=cron.find_command('setIPCamExpo.sh REBOOT')
    for i in iter:
        if i.is_enabled():
            found = True
    if found is False:
        job = cron.new(f'sleep 10 && {local_path}/setIPCamExpo.sh REBOOT > {rmslogdir}/setreboot.log 2>&1')
        job.every_reboot()
        cron.write()

    cron.write()
    print('cron jobs updated')
    return 


if __name__ == '__main__':

    srcdir = os.path.split(os.path.abspath(__file__))[0]
    arg_parser = argparse.ArgumentParser(description='Set camera to day or night mode')

    arg_parser.add_argument('daynight', nargs=1, metavar='DAYNIGHT', type=str,
        help='day or night mode')

    arg_parser.add_argument('-c', '--config', nargs=1, metavar='CONFIG_PATH', type=str, 
        help='Path to a config file which will be used instead of the default one.')

    arg_parser.add_argument('-n', '--nightcolour', action="store_true", help='use colour mode at night')
    
    arg_parser.add_argument('-a', '--autoexp', action="store_true", help='use autoexposure mode')
    
    arg_parser.add_argument('-g', '--nightgain', metavar='NIGHT_GAIN', help='night gain to use (default 70)')

    arg_parser.add_argument('-s', '--stationid', metavar='STATIONID', help='optional stationid if not in config.ini')

    cml_args = arg_parser.parse_args()

    daynight = cml_args.daynight[0].lower()

    localcfg = configparser.ConfigParser()
    if cml_args.config:
        localcfg.read(cml_args.config[0])
    else:
        localcfg.read(os.path.join(srcdir, 'config.ini'))

    nightgain = None
    if cml_args.nightgain and int(cml_args.nightgain) != 70:
        nightgain = int(cml_args.nightgain)

    nightColor = False
    if cml_args.nightcolour:
        nightColor = True

    autoexp = False
    if cml_args.autoexp:
        autoexp = True

    if cml_args.stationid:
        camids = [cml_args.stationid]
    else:
        camids = [x[1].upper() for x in localcfg.items('stations')]

    testmode = False
    for camid in camids: 
        try:
            cfg = getRMSConfig(camid, localcfg)
        except Exception:
            print(f'cfg file for {camid} not found, skipping')
            cfg = None
        if cfg is not None:
            setCameraExposure(cfg, daynight, nightgain=nightgain, nightColor=nightColor, autoExp=autoexp, testmode=testmode)
            addCrontabEntries(cfg, testmode=testmode)
