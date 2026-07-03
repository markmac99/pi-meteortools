# Copyright (C) 2018-2023 Mark McIntyre
#
# python code to read in an FTPdetect file and plot all the detections
#

import os
import configparser as cr 
from matplotlib import pyplot as plt
import sys


def _readFTPfile(filename, h):
    """ Internal function to load ftpfile into arrays """
    events = []
    with open(filename) as f:
        # Skip the header
        for i in range(11):
            next(f)

        for line in f:
            line = line.replace('\n', '').replace('\r', '')
            # The separator marks the beginning of a new meteor
            if "-------------------------------------------------------" in line:
                # Skip the event header
                for i in range(2):
                    next(f)
            # read line containing detail of this event
            line = f.readline()
            rows = int(line.split()[2])
            xvals=[]
            yvals=[]
            # now read in the data of interest
            for r in range(rows):
                line = f.readline()
                _, x, y, _, _, _, _, _ = list(map(float, line.split()[:8]))
                xvals.append(x)
                yvals.append(h-y)
            dta = {'x': xvals, 'y': yvals}
            events.append(dta)

    return events


def drawFTPFile(ftpfile, cfgfile=None):
    """
    Creates a simple representation of an FTPdetect file, showing the locations of each meteor trail.  
    Its like a stack of the night's detections but in a much simpler format. Useful for diagnosing false detections.   

    Arguments:  
        ftpfile:   [str] full path to the FTPdetect file.  
        cfgfile:   [str] full path to RMS config file to read image dimensions. Default is 1280x720.  
    """
    config = cr.ConfigParser()
    if cfgfile is None: 
        width=1280
        height=720
    else:
        config.read(cfgfile)
        width = int(config['Capture']['width'])
        height = int(config['Capture']['height'])

    print('plotting field of view {}x{}'.format(width, height))
    events = _readFTPfile(ftpfile, height)
    for ev in events: 
        plt.plot(ev['x'],ev['y'])
    pth, ftpf = os.path.split(ftpfile)
    spls = ftpf.split('_')
    outfname = f'{spls[1]}_{spls[2]}_{spls[3]}_{spls[3]}_ftpmap.png'
    print(f'saved to {outfname}')
    plt.savefig(os.path.join(pth, outfname))
    plt.close()
    return 


if __name__ == '__main__':
    drawFTPFile(sys.argv[1])