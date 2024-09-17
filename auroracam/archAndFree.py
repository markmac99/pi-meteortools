# copyright (c) Mark McIntyre, 2024-
#
# Python script to free diskspace on Auroracam
# 
import os
import configparser
from auroraCam import setupLogging, freeSpaceAndArchive

if __name__ == '__main__':
    thiscfg = configparser.ConfigParser()
    local_path = os.path.dirname(os.path.abspath(__file__))
    thiscfg.read(os.path.join(local_path, 'config.ini'))
    setupLogging(thiscfg, 'archive_')
    freeSpaceAndArchive(thiscfg)
