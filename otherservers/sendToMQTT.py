#
# Python script to publish diskspace and cputemp data to MQTT
# Copyright (C) Mark McIntyre
#
#

import paho.mqtt.client as mqtt
import os
import sys
import platform 
import logging
from crontab import CronTab
import configparser

log = logging.getLogger("logger")


def addCrontabs():
    local_path =os.path.dirname(os.path.abspath(__file__))
    cron = CronTab(user=True)
    for job in cron:
        if 'logToMQTT' in job.command:
            cron.remove(job)
            cron.write()
    job = cron.new(f'{local_path}/logToMQTT.sh >> /dev/null 2>&1')
    job.setall('*/5', '*', '*', '*', '*')
    cron.write()
    return 


# The callback function. It will be triggered when trying to connect to the MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected success")
    else:
        print("Connected fail with code", rc)


def on_publish(client, userdata, result):
    #print('data published - {}'.format(result))
    return


def sendOtherData(cputemp, diskspace, localcfg=None):
    if localcfg is None:
        srcdir = os.path.split(os.path.abspath(__file__))[0]
        localcfg = configparser.ConfigParser()
        localcfg.read(os.path.join(srcdir, 'config.ini'))
    broker = localcfg['mqtt']['broker']
    hname = platform.uname().node
    client = mqtt.Client(hname)
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
    topic = f'meteorcams/{hname}/cputemp'
    ret = client.publish(topic, payload=cputemp, qos=0, retain=False)
    topic = f'meteorcams/{hname}/diskspace'
    ret = client.publish(topic, payload=diskspace, qos=0, retain=False)
    return ret


def test_mqtt(localcfg=None):
    if localcfg is None:
        srcdir = os.path.split(os.path.abspath(__file__))[0]
        localcfg = configparser.ConfigParser()
        localcfg.read(os.path.join(srcdir, 'config.ini'))
    broker = localcfg['mqtt']['broker']
    hname = platform.uname().node
    topic = f'testing/{hname}/test'
    client = mqtt.Client(hname)
    client.on_connect = on_connect
    client.on_publish = on_publish
    if localcfg['mqtt']['username'] != '':
        client.username_pw_set(localcfg['mqtt']['username'], localcfg['mqtt']['password'])
    client.connect(broker, 1883, 60)
    ret = client.publish(topic, payload=f'test from {hname}', qos=0, retain=False)
    print("send to {}, result {}".format(topic, ret))


if __name__ == '__main__':
    if sys.argv[1] == 'test':
        test_mqtt()
    else:
        print('no direct usage')
