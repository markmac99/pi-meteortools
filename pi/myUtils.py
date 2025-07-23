# Copyright (C) Mark McIntyre
#
# utility functions

import RMS.ConfigReader as cr
import os


def getRMSConfig(statid, localcfg):
    rmscfg = os.path.expanduser(f'~/source/Stations/{statid}/.config')
    if not os.path.isfile(rmscfg):
        rmscfg = os.path.join(localcfg['postprocess']['rmsdir'], '.config')
    cfg = cr.parse(os.path.expanduser(rmscfg))
    return cfg
