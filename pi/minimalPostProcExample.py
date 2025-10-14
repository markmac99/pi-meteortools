# minimal RMS postprocessing hook
# copyright (c) mark mcintyre, 2025

import os


def rmsExternal(cap_dir, arch_dir, config):
    rebootlockfile = os.path.join(config.data_dir, config.reboot_lock_file)
    with open(rebootlockfile, 'w') as f:
        f.write('1')
    # do your station specific stuff here
    os.remove(rebootlockfile)
    return
