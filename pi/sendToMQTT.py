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
import requests
import configparser

try:
    import RMS.ConfigReader as cr
except Exception:
    pass

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

    logf = logfs[-1]
    lis = open(logf,'r').readlines()
    sc = [li for li in lis if 'Detected stars' in li]
    starcount = 0
    if len(sc) > 0:
        try:
            starcount = int(sc[-1].split()[5])
        except Exception:
            pass

    capdir = os.path.join(cfg.data_dir, 'CapturedFiles')
    caps = glob.glob(os.path.join(capdir, f'{cfg.stationID}*'))
    caps.sort(key=lambda x: os.path.getmtime(x))
    try:
        capdir = caps[-1]
        ftpfs = glob.glob(os.path.join(capdir, 'FTPdetectinfo*.txt'))
        ftpf = [f for f in ftpfs if 'backup' not in f and 'unfiltered' not in f]
        meteorcount = 0
        if len(ftpf) > 0:
            lis = open(ftpf[0],'r').readlines()
            mc = [li for li in lis if 'Meteor Count' in li]
            meteorcount = int(mc[0].split('=')[1].strip())
    except Exception:
        # probably no captured data yet
        meteorcount = 0    
    # if meteorcount is nonzero but detected count is zero then the logfile was malformed
    if detectedcount == 0:
        detectedcount = meteorcount

    datestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    return detectedcount, meteorcount, starcount, datestamp


def sendMatchdataToMqtt(rmscfg=None, localcfg=None):
    if localcfg is None:
        srcdir = os.path.split(os.path.abspath(__file__))[0]
        localcfg = configparser.ConfigParser()
        localcfg.read(os.path.join(srcdir, 'config.ini'))
    if rmscfg is None:
        rmscfg = os.path.join(localcfg['postprocess']['rmsdir'], '.config')
    cfg = cr.parse(os.path.expanduser(rmscfg))
    broker = localcfg['mqtt']['broker']
    topicbase = 'meteorcams' 
    camname = cfg.stationID.lower()
    apiurl = 'https://api.ukmeteors.co.uk/matches'
    dtstr = datetime.datetime.now().strftime('%Y%m%d')
    apicall = f'{apiurl}?reqtyp=station&reqval={dtstr}&statid={cfg.stationID}'
    res = requests.get(apicall)
    if res.status_code == 200:
        rawdata=res.text.strip()
        matchcount = rawdata.count('orbname')
    else:
        matchcount = 0
    dtstr = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y%m%d')
    apicall = f'{apiurl}?reqtyp=station&reqval={dtstr}&statid={cfg.stationID}'
    res = requests.get(apicall)
    if res.status_code == 200:
        rawdata=res.text.strip()
        v1 = rawdata.count(f'{dtstr}_1')
        v2 = rawdata.count(f'{dtstr}_2')
        matchcount = matchcount + v1 + v2
    client = mqtt.Client(camname)
    client.on_connect = on_connect
    client.on_publish = on_publish
    if localcfg['mqtt']['username'] != '':
        client.username_pw_set(localcfg['mqtt']['username'], localcfg['mqtt']['password'])
    client.connect(broker, 1883, 60)
    topic = f'{topicbase}/{camname}/matchcount'
    ret = client.publish(topic, payload=matchcount, qos=0, retain=False)
    log.info(f'there were {matchcount} matches last night for {camname}')
    return ret


def sendToMqtt(rmscfg=None, localcfg=None):
    if localcfg is None:
        srcdir = os.path.split(os.path.abspath(__file__))[0]
        localcfg = configparser.ConfigParser()
        localcfg.read(os.path.join(srcdir, 'config.ini'))
    if rmscfg is None:
        rmscfg = os.path.join(localcfg['postprocess']['rmsdir'], '.config')
    cfg = cr.parse(os.path.expanduser(rmscfg))
    broker = localcfg['mqtt']['broker']
    topicbase = 'meteorcams' 
    camname = cfg.stationID.lower()

    metcount, detectioncount, _, datestamp = getLoggedInfo(cfg)
    msgs =[metcount, detectioncount, datestamp]

    client = mqtt.Client(camname)
    client.on_connect = on_connect
    client.on_publish = on_publish
    if localcfg['mqtt']['username'] != '':
        client.username_pw_set(localcfg['mqtt']['username'], localcfg['mqtt']['password'])
    client.connect(broker, 1883, 60)

    subtopics = ['detectioncount','meteorcount','timestamp']
    for subtopic, msg in zip(subtopics, msgs): 
        topic = f'{topicbase}/{camname}/{subtopic}'
        ret = client.publish(topic, payload=msg, qos=0, retain=False)
        #print("send to {}, result {}".format(topic, ret))
    return ret


def sendStarCountToMqtt(rmscfg=None, localcfg=None):
    if localcfg is None:
        srcdir = os.path.split(os.path.abspath(__file__))[0]
        localcfg = configparser.ConfigParser()
        localcfg.read(os.path.join(srcdir, 'config.ini'))
    if rmscfg is None:
        rmscfg = os.path.join(localcfg['postprocess']['rmsdir'], '.config')
    cfg = cr.parse(os.path.expanduser(rmscfg))
    broker = localcfg['mqtt']['broker']
    topicbase = 'meteorcams' 
    camname = cfg.stationID.lower()
    _, _, starcount, _ = getLoggedInfo(cfg)
    client = mqtt.Client(camname)
    client.on_connect = on_connect
    client.on_publish = on_publish
    if localcfg['mqtt']['username'] != '':
        client.username_pw_set(localcfg['mqtt']['username'], localcfg['mqtt']['password'])
    client.connect(broker, 1883, 60)

    topic = f'{topicbase}/{camname}/starcount'
    print(f'starcount is {starcount}')
    ret = client.publish(topic, payload=starcount, qos=0, retain=False)
    return ret


def sendOtherData(cputemp, diskspace, rmscfg=None, localcfg=None):
    if localcfg is None:
        srcdir = os.path.split(os.path.abspath(__file__))[0]
        localcfg = configparser.ConfigParser()
        localcfg.read(os.path.join(srcdir, 'config.ini'))
    if rmscfg is None:
        rmscfg = os.path.join(localcfg['postprocess']['rmsdir'], '.config')
    cfg = cr.parse(os.path.expanduser(rmscfg))
    broker = localcfg['mqtt']['broker']
    camname = cfg.stationID.lower()

    client = mqtt.Client(camname)
    client.on_connect = on_connect
    client.on_publish = on_publish
    if localcfg['mqtt']['username'] != '':
        client.username_pw_set(localcfg['mqtt']['username'], localcfg['mqtt']['password'])
    client.connect(broker, 1883, 60)
    if len(cputemp) > 2:
        cputemp = cputemp[:-2]
    else:
        cputemp = 0
    if len(diskspace) > 1:
        diskspace = diskspace[:-1]
    else:
        diskspace = 0
    topic = f'meteorcams/{camname}/cputemp'
    ret = client.publish(topic, payload=cputemp, qos=0, retain=False)
    topic = f'meteorcams/{camname}/diskspace'
    ret = client.publish(topic, payload=diskspace, qos=0, retain=False)
    return ret


def test_mqtt(rmscfg=None, localcfg=None):
    if localcfg is None:
        srcdir = os.path.split(os.path.abspath(__file__))[0]
        localcfg = configparser.ConfigParser()
        localcfg.read(os.path.join(srcdir, 'config.ini'))
    if rmscfg is None:
        rmscfg = os.path.join(localcfg['postprocess']['rmsdir'], '.config')
    cfg = cr.parse(os.path.expanduser(rmscfg))
    broker = localcfg['mqtt']['broker']
    camname = cfg.stationID.lower()

    client = mqtt.Client(camname)
    topic = f'testing/{camname}/test'
    client.on_connect = on_connect
    client.on_publish = on_publish
    if localcfg['mqtt']['username'] != '':
        client.username_pw_set(localcfg['mqtt']['username'], localcfg['mqtt']['password'])
    client.connect(broker, 1883, 60)
    ret = client.publish(topic, payload=f'test from {camname}', qos=0, retain=False)
    print("send to {}, result {}".format(topic, ret))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_mqtt(None, None)
    else:
        sendToMqtt(None, None)
