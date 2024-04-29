# SetExpo.py
# sets the exposure on the IPCamera using Python_DVRIP
# Copyright (C) Mark McIntyre
#
#
import time

# if you have RMS and the ukmon-pitools installed, these libs will already be present
from dvrip import DVRIPCam


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
