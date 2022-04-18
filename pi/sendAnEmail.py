# 
# Send email from python
#
import os
import platform
import configparser
import base64
#import lxml.html
import logging
#from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
#from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES =['https://mail.google.com/']


def getGmailCreds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    tokfile = os.path.expanduser('~/.ssh/gmailtoken.json')
    crdfile = os.path.expanduser('~/.ssh/gmailcreds.json')
    if os.path.exists(tokfile):
        creds = Credentials.from_authorized_user_file(tokfile, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(crdfile, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokfile, 'w') as token:
            token.write(creds.to_json())
    return creds


def create_message(sender, to, subject, message_text):
    msg = MIMEText(message_text)
    msg['to'] = to
    msg['from'] = sender
    msg['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode('utf-8')).decode('utf-8')}


def sendDailyMail(localcfg, hname, curdt, total, extramsg, log):

    creds = getGmailCreds()
    service = build('gmail', 'v1', credentials=creds)

    mailrecip = localcfg['postprocess']['mailrecip'].rstrip()
    if len(mailrecip)<5:
        mailrecip ='mark.jm.mcintyre@cesmail.net'
    message = '{:s}: {:s}: {:d} meteors found'.format(hname, curdt, total)
    message = message + '\n' + extramsg
    mailmsg = create_message('markmcintyre99@gmail.com',mailrecip,
        '{:s}: {:s}: {:d} meteors found'.format(hname, curdt, total), message)
    try:
        retval = (service.users().messages().send(userId='me', body=mailmsg).execute())
        print('Message Id: %s' % retval['id'])
    except:
        print('An error occurred sending the message')


if __name__ == '__main__':
    srcdir = os.path.split(os.path.abspath(__file__))[0]
    localcfg = configparser.ConfigParser()
    localcfg.read(os.path.join(srcdir, 'config.ini'))
    hname = platform.uname().node
    curdt = '2021-05-01'

    log = logging.getLogger("logger")
    sendDailyMail(localcfg, hname, curdt, 1, '', log)
