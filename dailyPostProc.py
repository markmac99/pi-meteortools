#!/usr/bin/env python 
# python script thats called when the nightly run completes
#

import os
import shutil
import glob
import configparser

import Utils.StackFFs as sff
import Utils.BatchFFtoImage as bff2i
import Utils.GenerateMP4s as gmp4
import Utils.generateTimelapse as gti


def rmsExternal(cap_dir, arch_dir, config):
    rebootlockfile = os.path.join(config.data_dir, config.reboot_lock_file)
    with open(rebootlockfile, 'w') as f:
        f.write('1')

    localcfg = configparser.ConfigParser()
    localcfg.read('/home/pi/mjmm/config.ini')
    srcdir = localcfg['postprocess']['scriptdir']

    # stack and create jpgs from the potential detections
    sff.StackFFs(arch_dir, 'jpg', filter_bright=True)
    bff2i.BatchFFtoImage(arch_dir, 'jpg')

    # generate MP4s of detections
    ftpdate=''
    if os.path.split(arch_dir)[1] == '':
        ftpdate=os.path.split(os.path.split(arch_dir)[0])[1]
    else:
        ftpdate=os.path.split(arch_dir)[1]
    ftpfile_name="FTPdetectinfo_"+ftpdate+'.txt'
    gmp4.GenerateMP4s(arch_dir, ftpfile_name)

    # generate an all-night timelapse and move it to arch_dir
    gti.generateTimelapse(cap_dir, False)
    mp4name = os.path.basename(cap_dir) + '.mp4'
    shutil.move(os.path.join(cap_dir, mp4name), os.path.join(arch_dir, mp4name))
    
    # upload timelapse to Youtube
    with open(os.path.join(srcdir, '.ytdone'), 'r') as f:
        line = f.readline()
        if line != mp4name:
            tod = mp4name.split('_')[1]
            cmdline = '/home/pi/vRMS/bin/python '
            cmdline += '{:s}/sendToYoutube.py '.format(srcdir)
            cmdline += '"`hostname` timelapse for {:s}" {:s}'.format(tod, mp4name)
            os.system(cmdline)
        with open(os.path.join(srcdir, '.ytdone'), 'w') as f:
            f.write(mp4name + '\n')

    # upload the MP4 to S3 or a website
    if localcfg['postprocess']['upload'] ==1:
        hn = localcfg['postprocess']['host']
        fn = os.path.join(arch_dir, mp4name)
        splits = mp4name.split('_')
        stn = splits[0]
        yymm = splits[1]
        yymm = splits[:6]
        if hn[:3] == 's3:':
            cmdline = 'aws s3 cp {:s} {:s}/{:s}/{:s}/{:s}'.format(fn, hn, stn, yymm, mp4name)
            os.system(cmdline)
        else:
            idfile = localcfg['postporocess']['idfile']
            user = localcfg['postporocess']['user']
            mp4dir = localcfg['postporocess']['mp4dir']
            cmdline = 'ssh -i {:s}  {:s}@{:s} mkdir {:s}/{:s}/{:s}'.format(idfile, user, hn, mp4dir, stn, yymm)
            os.system(cmdline)
            cmdline = 'scp-i {:s} {:s} {:s}@{:s} mkdir {:s}/{:s}/{:s}'.format(idfile, fn, user, hn, mp4dir, stn, yymm)
            os.system(cmdline)

    # if mmsmtp is installed email a summary out
    if os.path.isfile('/usr/bin/msmtp') and os.path.isfile('/usr/bin/bc'):
        logdir = os.path.expanduser(os.path.join(config.data_dir, config.log_dir))
        splits = os.path.basename(arch_dir).split('_')
        curdt = splits[1]
        logname=os.path.join(logdir, 'log_' + splits[1] + '_' + '*.log')
        logfs = glob.glob(logname)
        total = 0
        for f in logfs:
            with open(f,'r') as fi:
                sl = fi.readlines()
                for line in sl:
                    if 'TOTAL' in line:
                        total = int(line.split[4])
        with open('/tmp/message.txt', 'w') as msgfile:
            hname = os.uname()[1]
            msgfile.write('From: pi@{:s}\n'.format(hname))
            msgfile.write('To: {:s}\n'.format(localcfg['postprocess']['mailrecip']))
            msgfile.write('Subject: {:s}: {:s}: {:d} meteors found'.format(hname, curdt, total))

        os.system('/usr/bin/msmtp -t  < /tmp/message.txt')

    # reboot the camera
    os.system('python3 -m Utils.CameraControl reboot')

    # TODO: log the number of FFs and  hours

    os.remove(rebootlockfile)
    return


if __name__ == '__main__':
    cap_dir = '/tmp'
    arch_dir = '/tmp'

    class cfg(object):
        pass
    cnf = cfg()
    cnf.reboot_lock_file = '.reboot_lock'
    cnf.data_dir = '/tmp'

    rmsExternal(cap_dir, arch_dir, cnf)
