# 
# python script thats called when the nightly run completes
#

import os
import sys
import glob
import configparser

import RMS.ConfigReader as cr

import boto3

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def rmsExternal(cap_dir, arch_dir, config):
    rebootlockfile = os.path.join(config.data_dir, config.reboot_lock_file)
    with open(rebootlockfile, 'w') as f:
        f.write('1')

    print('reading local config')
    srcdir = os.path.split(os.path.abspath(__file__))[0]
    localcfg = configparser.ConfigParser()
    localcfg.read(os.path.join(srcdir, 'config.ini'))
    sys.path.append(srcdir)
    hname = os.uname()[1]
    import sendToYoutube as stu

    extramsg = 'Notes:\n'
    # upload mp4 to youtube
    try: 
        mp4name = os.path.basename(cap_dir) + '.mp4'

        if not os.path.isfile(os.path.join(srcdir, '.ytdone')):
            with open(os.path.join(srcdir, '.ytdone'), 'w') as f:
                f.write('dummy\n')

        with open(os.path.join(srcdir, '.ytdone'), 'r') as f:
            line = f.readline().rstrip()
            if line != mp4name:
                tod = mp4name.split('_')[1]
                tod = tod[:4] +'-'+ tod[4:6] + '-' + tod[6:8]
                msg = '{:s} timelapse for {:s}'.format(hname, tod)
                print('uploading {:s} to youtube'.format(mp4name))
                stu.main(msg, os.path.join(arch_dir, mp4name))
            else:
                print('already uploaded {:s}'.format(mp4name))
                
            with open(os.path.join(srcdir, '.ytdone'), 'w') as f:
                f.write(mp4name)

        # upload the MP4 to S3 or a website
        if int(localcfg['postprocess']['upload']) == 1:
            hn = localcfg['postprocess']['host']
            fn = os.path.join(arch_dir, mp4name)
            splits = mp4name.split('_')
            stn = splits[0]
            yymm = splits[1]
            yymm = yymm[:6]
            idfile = os.path.expanduser(localcfg['postprocess']['idfile'])
            if hn[:3] == 's3:':
                print('uploading to {:s}/{:s}/{:s}'.format(hn, stn, yymm))

                with open(idfile, 'r') as f:
                    li = f.readline()
                    key = li.split('=')[1].rstrip().strip('"')
                    li = f.readline()
                    secret = li.split('=')[1].rstrip().strip('"')

                s3 = boto3.resource('s3', aws_access_key_id = key, aws_secret_access_key = secret, 
                    region_name='eu-west-2')
                target=hn[5:]
                outf = '{:s}/{:s}/{:s}'.format(stn, yymm, mp4name)
                s3.meta.client.upload_file(fn, target, outf)
            else:
                print('uploading to website')
                user = localcfg['postprocess']['user']
                mp4dir = localcfg['postprocess']['mp4dir']
                cmdline = 'ssh -i {:s}  {:s}@{:s} mkdir {:s}/{:s}/{:s}'.format(idfile, user, hn, mp4dir, stn, yymm)
                os.system(cmdline)
                cmdline = 'scp -i {:s} {:s} {:s}@{:s} mkdir {:s}/{:s}/{:s}'.format(idfile, fn, user, hn, mp4dir, stn, yymm)
                os.system(cmdline)
    except:
        errmsg = 'unable to upload timelapse'
        print(errmsg)
        extramsg = extramsg + errmsg + '\n'

    # email a summary to the mailrecip
    mailrecip = localcfg['postprocess']['mailrecip'].rstrip()
    smtphost = localcfg['postprocess']['mailhost'].rstrip()
    smtpport = int(localcfg['postprocess']['mailport'].rstrip())
    smtpuser = localcfg['postprocess']['mailuser'].rstrip()
    smtppwd = localcfg['postprocess']['mailpwd'].rstrip()
    with open(os.path.expanduser(smtppwd), 'r') as fi:
        line = fi.readline()
        spls=line.split('=')
        smtppass=spls[1].rstrip()

    s = smtplib.SMTP(smtphost, smtpport)
    s.starttls()
    s.login(smtpuser, smtppass)
    msg = MIMEMultipart()

    msg['From']='pi@{:s}'.format(hname)
    msg['To']=mailrecip

    logdir = os.path.expanduser(os.path.join(config.data_dir, config.log_dir))
    splits = os.path.basename(arch_dir).split('_')
    curdt = splits[1]
    logname=os.path.join(logdir, 'log_' + splits[1] + '_' + '*.log*')
    logfs = glob.glob(logname)
    total = 0
    for f in logfs:
        with open(f,'r') as fi:
            sl = fi.readlines()
            for line in sl:
                if 'TOTAL' in line:
                    ss = line.split(' ')
                    total = total + int(ss[4])

    msg['Subject']='{:s}: {:s}: {:d} meteors found'.format(hname, curdt, total)
    message = '{:s}: {:s}: {:d} meteors found'.format(hname, curdt, total)
    message = message + '\n' + extramsg
    msg.attach(MIMEText(message, 'plain'))
    s.sendmail(msg['From'], mailrecip, msg.as_string())
    s.close()

    os.remove(rebootlockfile)
    return


if __name__ == '__main__':
    hname = os.uname()[1]
    if len(sys.argv) < 1:
        if hname == 'meteorpi':
            cap_dir = '/home/pi/RMS_data/CapturedFiles/UK0006_20210130_172616_214463'
            arch_dir = '/home/pi/RMS_data/ArchivedFiles/UK0006_20210130_172616_214463'
        else:
            cap_dir = '/home/pi/RMS_data/CapturedFiles/UK000F_20210128_172253_791467'
            arch_dir = '/home/pi/RMS_data/ArchivedFiles/UK000F_20210128_172253_791467'
    else:
        cap_dir = os.path.join('/home/pi/RMS_data/CapturedFiles/', sys.argv[1])
        arch_dir = os.path.join('/home/pi/RMS_data/ArchivedFiles/', sys.argv[1])

    config = cr.parse(".config")

    rmsExternal(cap_dir, arch_dir, config)