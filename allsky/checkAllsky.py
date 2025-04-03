# python script to check and restart the allsky camera if needed
# copyright Mark McIntyre 2025-

import os
import datetime
import time
import logging
from logging.handlers import RotatingFileHandler

log = logging.getLogger('checkAllsky')

MAXDELAY = 120      # time to wait to rebood
SUPERMAXDELAY=1800  # wait 30 mins to create timelapse in case its still working


def hasStalled(dt, logfile):
    loglines = open(logfile, 'r').readlines()
    lastline = loglines[-1][:19]
    lastdt = datetime.datetime.strptime(lastline, '%Y-%m-%dT%H:%M:%S')
    dtstr = datetime.datetime.strftime(dt, '%Y-%m-%d')
    tllines = [li for li in loglines if 'Timelapse' in li]
    dtdlines = [li for li in tllines if dtstr in li]
    if len(dtdlines) == 1:
        return (datetime.datetime.now()-lastdt).seconds > SUPERMAXDELAY
    return (datetime.datetime.now()-lastdt).seconds > MAXDELAY


if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    fh = RotatingFileHandler(os.path.expanduser('LOGDIR/checkAllsky.log'), maxBytes=51200, backupCount=10)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    log.addHandler(fh)
    stopfile = os.path.expanduser('LOGDIR/stopcheckallsky')

    if os.path.isfile(stopfile):
        os.remove(stopfile)
    runme = True
    log.info('starting')
    while runme is True:
        log.info('checking')
        if hasStalled(datetime.datetime.now(), '/var/log/allsky.log'):
            log.info('stuck, rebooting')
            os.system('sudo reboot now')
            
        if os.path.isfile(stopfile):
            os.remove(stopfile)
            log.info('quitting')
            runme = False
        else:
            log.info('sleeping')
            time.sleep(MAXDELAY)
