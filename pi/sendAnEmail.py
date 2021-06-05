# 
# Send email from python
#
import os
import configparser
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendDailyMail(localcfg, hname, curdt, total, extramsg, log):

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

    msg['Subject']='{:s}: {:s}: {:d} meteors found'.format(hname, curdt, total)
    message = '{:s}: {:s}: {:d} meteors found'.format(hname, curdt, total)
    message = message + '\n' + extramsg
    msg.attach(MIMEText(message, 'plain'))
    try:
        log.info('invoking sendmail')
        s.sendmail(msg['From'], mailrecip, msg.as_string())
    except:
        log.info('unable to send mail')

    s.close()


if __name__ == '__main__':
    srcdir = os.path.split(os.path.abspath(__file__))[0]
    localcfg = configparser.ConfigParser()
    localcfg.read(os.path.join(srcdir, 'config.ini'))
    hname = os.uname()[1]
    curdt = '2021-05-01'

    log = logging.getLogger("logger")
    sendDailyMail(localcfg, hname, curdt, 1, '', log)
