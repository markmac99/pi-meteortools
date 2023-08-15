#
# Python script to publish meteor data to MQTT
# Copyright (C) Mark McIntyre
#
#
# first run "pip install paho-mqtt"
# then run "python sendToMQTT.py"
# it will create topics:
#   meteorcams/youcamid/detectedcount
#   meteorcams/youcamid/meteorcount
#   meteorcams/youcamid/datestamp
# Which are respectively, the total reported in the log file, the total in the FTPdetect file, 
# and the time the script ran at

import paho.mqtt.client as mqtt
import datetime
import os
import sys
import glob
import platform 
import logging

import RMS.ConfigReader as cr

log = logging.getLogger("logger")


# The callback function. It will be triggered when trying to connect to the MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected success")
    else:
        print("Connected fail with code", rc)


def on_publish(client, userdata, result):
    #print('data published - {}'.format(result))
    return


def getLoggedInfo(cfg):
    log_dir = os.path.join(cfg.data_dir, cfg.log_dir)
    logfs = glob.glob(os.path.join(log_dir, 'log*.log*'))
    logfs.sort(key=lambda x: os.path.getmtime(x))
    dd=[]
    i=1
    while len(dd) == 0 and i < 10:
        logf = logfs[-i]
        lis = open(logf,'r').readlines()
        dd = [li for li in lis if 'Data directory' in li]
        if len(dd) > 0:
            break
        i = i + 1

    totli = [li for li in lis if 'TOTAL' in li]
    detectedcount = 0
    if len(totli) > 0:
        detectedcount = int(totli[0].split(' ')[4].strip())

    capdir = os.path.join(cfg.data_dir, 'CapturedFiles')
    caps = glob.glob(os.path.join(capdir, f'{cfg.stationID}*'))
    caps.sort(key=lambda x: os.path.getmtime(x))
    capdir = caps[-1]
    ftpfs = glob.glob(os.path.join(capdir, 'FTPdetectinfo*.txt'))
    ftpf = [f for f in ftpfs if 'backup' not in f and 'unfiltered' not in f]
    meteorcount = 0
    if len(ftpf) > 0:
        lis = open(ftpf[0],'r').readlines()
        mc = [li for li in lis if 'Meteor Count' in li]
        meteorcount = int(mc[0].split('=')[1].strip())
    
    # if meteorcount is nonzero but detected count is zero then the logfile was malformed
    if detectedcount == 0:
        detectedcount = meteorcount

    datestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    return detectedcount, meteorcount, datestamp


def sendToMqtt(cfg, localcfg=None):
    if localcfg is None:
        broker = 'wxsatpi' # localcfg['mqtt']['broker']
    else:
        broker = localcfg['mqtt']['broker']
    topicbase = 'meteorcams' 
    camname = cfg.stationID.lower()

    metcount, detectioncount, datestamp = getLoggedInfo(cfg)
    msgs =[metcount, detectioncount, datestamp]

    client = mqtt.Client(camname)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(broker, 1883, 60)

    subtopics = ['detectioncount','meteorcount','timestamp']
    for subtopic, msg in zip(subtopics, msgs): 
        topic = f'{topicbase}/{camname}/{subtopic}'
        ret = client.publish(topic, payload=msg, qos=0, retain=False)
        #print("send to {}, result {}".format(topic, ret))
    return ret


def sendOtherData(cputemp, diskspace, localcfg=None):
    if localcfg is None:
        broker = 'wxsatpi'
    else:
        broker = localcfg['mqtt']['broker']
    hname = platform.uname().node
    client = mqtt.Client(hname)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(broker, 1883, 60)
    if len(cputemp) > 2:
        cputemp = cputemp[:-2]
    else:
        cputemp = 0
    if len(diskspace) > 1:
        diskspace = diskspace[:-1]
    else:
        diskspace = 0
    topic = f'meteorcams/{hname}/cputemp'
    ret = client.publish(topic, payload=cputemp, qos=0, retain=False)
    topic = f'meteorcams/{hname}/diskspace'
    ret = client.publish(topic, payload=diskspace, qos=0, retain=False)
    return ret


def test_mqtt(localcfg=None):
    if localcfg is None:
        broker = 'wxsatpi'
    else:
        broker = localcfg['mqtt']['broker']
    hname = platform.uname().node
    topic = f'testing/{hname}/test'
    client = mqtt.Client(hname)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.connect(broker, 1883, 60)
    ret = client.publish(topic, payload=f'test from {hname}', qos=0, retain=False)
    print("send to {}, result {}".format(topic, ret))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        rmscfg = '/home/pi/source/RMS/.config'
    else:
        rmscfg = sys.argv[1]
    if rmscfg == 'test':
        test_mqtt()
    else:
        cfg = cr.parse(os.path.expanduser(rmscfg))
        localcfg = None
        sendToMqtt(cfg, localcfg)
