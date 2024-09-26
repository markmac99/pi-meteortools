# SetExpo.py
# sets the exposure on the IPCamera using Python_DVRIP
# Copyright (C) Mark McIntyre
#
#
import time

# if you have RMS and the ukmon-pitools installed, these libs will already be present
from dvrip import DVRIPCam
import ipaddress
import binascii
import socket
import pprint
from time import sleep


def connectToCam(host_ip):
    cam = DVRIPCam(host_ip)
    print('connecting to', host_ip)
    for i in range(0,5):
        try: 
            if cam.login():
                print("Success! Connected to " + host_ip)
                break
        except:
            print("Failure. Could not connect. retrying in 30 seconds")
            time.sleep(30)
    if i == 4:
        print('unable to connect to camera, aborting')
        exit(1)
    return cam


def setCameraExposure(host_ip, daynight, nightgain=70, nightColor=False, autoExp=False):
    daycmode = '0x00000001'
    nightcmode = '0x00000002'
    if nightColor is True:
        nightcmode = daycmode

    if daynight == 'DAY':
        expo = 30
        gain = 30
        cmode = daycmode
        minexp = '0x00000064'
        maxexp = '0x00009C40'
    else:
        cmode = nightcmode
        gain = nightgain
        if autoExp is True:
            expo = 30
            minexp = '0x00000064'
        else:
            expo = 100
            minexp = '0x00009C40'
        maxexp = '0x00009C40'

    cam = connectToCam(host_ip)
    params = cam.get_info("Camera")
    print(params['Param'])
    print(params['Param'][0]['ElecLevel'])

    cam.set_info("Camera.Param.[0]",{"ElecLevel":expo})
    cam.set_info("Camera.Param.[0]",{"DayNightColor":cmode})
    cam.set_info("Camera.Param.[0].GainParam",{"Gain":gain})
    cam.set_info("Camera.Param.[0].ExposureParam",{"LeastTime":minexp})
    cam.set_info("Camera.Param.[0].ExposureParam",{"MostTime":maxexp})
    params = cam.get_info("Camera")
    print(params['Param'][0]['ElecLevel'])

    cam.close()


def strIPtoHex(ip):
    a = binascii.hexlify(socket.inet_aton(ip)).decode().upper()
    addr='0x'+''.join([a[x:x+2] for x in range(0,len(a),2)][::-1])
    return addr


def hexIPtoStr(s):
    a=s[2:]
    addr='0x'+''.join([a[x:x+2] for x in range(0,len(a),2)][::-1])
    ipaddr=ipaddress.IPv4Address(int(addr,16))
    return ipaddr


def getCameraNetWorkDets(host_ip):
    cam = connectToCam(host_ip)
    nc=cam.get_info("NetWork.NetCommon")
    print(hexIPtoStr(nc['HostIP']))
    dh = cam.get_info("NetWork.NetDHCP")
    pprint.pprint(dh)
    return


def rebootCamera(host_ip):
    cam = connectToCam(host_ip)
    cam.reboot()
    print('rebooting, please wait....')
    sleep(5) # wait while camera starts
    cam.login()
    print('reboot successful')
    return 


def setCameraNetWorkDets(host_ip, new_ip=None, dhcpon=0):
    cam = connectToCam(host_ip)
    if new_ip:
        cam.set_info("NetWork.NetCommon.HostIP", strIPtoHex(new_ip))
        cam.set_info("NetWork.NetCommon.Submask", strIPtoHex('255.255.255.0'))
    if dhcpon == 1:
        cam.set_info("NetWork.NetDHCP.[0].Enable", 1)
    elif dhcpon == -1:
        cam.set_info("NetWork.NetDHCP.[0].Enable", 0)
    return
