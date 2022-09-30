# SetExpo.py
# sets the exposure on the IPCamera using Python_DVRIP
#
import sys
import time
from dvrip import DVRIPCam


def setCameraExposure(host_ip, daynight, nightgain=70, nightColor=False):
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
        expo = 100
        gain = nightgain
        cmode = nightcmode
        minexp = '0x00009C40'
        maxexp = '0x00009C40'

    cam = DVRIPCam(host_ip)
    print('connecting to', host_ip)
    for i in range(5):
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


if __name__ == '__main__':
    host_ip = sys.argv[1]
    daynight=sys.argv[2]

    if len(sys.argv) > 3:
        nightgain = float(sys.argv[3])
    else:
        nightgain = 60

    if len(sys.argv) > 4:
        nightColor = True
    else:
        nightColor = False
    setCameraExposure(host_ip, daynight, nightgain, nightColor)

#[{'AeSensitivity': 1, 'ApertureMode': '0x00000000', 'BLCMode': '0x00000001', 
# 'DayNightColor': '0x00000002', 'Day_nfLevel': 0, 'DncThr': 50, 'ElecLevel': 30, 
# 'EsShutter': '0x00000006', 
# 'ExposureParam': {'LeastTime': '0x00000064', 'Level': 0, 'MostTime': '0x00013880'}, 
# 'GainParam': {'AutoGain': 1, 'Gain': 65}, 
# 'IRCUTMode': 0, 'IrcutSwap': 0, 'Night_nfLevel': 0, 
# 'PictureFlip': '0x00000001', 'PictureMirror': '0x00000001', 
# 'RejectFlicker': '0x00000000', 'WhiteBalance': '0x00000002'}]

# 'DayNightColor': '0x00000002' BW
# 'DayNightColor': '0x00000001' Colour

# 0.1ms 40ms 80ms
# '0x00000064'
# '0x00009C40'
# '0x00013880'
