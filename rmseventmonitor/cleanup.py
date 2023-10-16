# Copyright (c) Mark McIntyre 2023-
import os
import sys
import shutil
import glob


def filterData(dirnam):
    goodcams = glob.glob1(os.path.join(dirnam, 'stacks'), '*.jpg')
    goodcams = [x[:6] for x in goodcams]
    os.makedirs(os.path.join(dirnam, 'nogood'), exist_ok=True)
    allcams = glob.glob1(dirnam, '*')
    allcams = [x for x in allcams if '.bz2' not in x]
    allcams = [x for x in allcams if '.zip' not in x]
    allcams = [x for x in allcams if 'jpgs' not in x]
    allcams = [x for x in allcams if 'stacks' not in x]
    allcams = [x for x in allcams if 'mp4s' not in x]
    allcams = [x for x in allcams if 'nogood' not in x]
    allcams = [x for x in allcams if 'trajectories' not in x]

    movecams = [x for x in allcams if x not in goodcams]
    for cam in movecams:
        print(f'checking {cam}')
        shutil.move(os.path.join(dirnam, cam), os.path.join(dirnam, 'nogood'))
        cambzs = glob.glob(os.path.join(dirnam,f'{cam}*.bz2'))
        for thiscam in cambzs:
            shutil.move(thiscam, os.path.join(dirnam, 'nogood'))
        jpgs = glob.glob(os.path.join(dirnam,'jpgs',f'*{cam}*.jpg'))
        for jpg in jpgs:
            shutil.move(jpg, os.path.join(dirnam, 'nogood'))
        mp4s = glob.glob(os.path.join(dirnam,'mp4s',f'*{cam}*.jpg'))
        for mp4 in mp4s:
            shutil.move(mp4, os.path.join(dirnam, 'nogood'))
    for cambz in glob.glob1(dirnam,'*.bz2'):
        camid = cambz[:6]
        if camid not in goodcams: 
            shutil.move(os.path.join(dirnam, cambz), os.path.join(dirnam, 'nogood'))


if __name__ == '__main__':
    filterData(sys.argv[1])
