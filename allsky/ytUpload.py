# -*- coding: utf-8 -*-

import os, sys
import pickle
import datetime
from time import sleep
from crontab import CronTab
import ephem

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

scopes = ["https://www.googleapis.com/auth/youtube.upload"]


def uploadToYoutube(here, title, fname):
    # set to 1 to disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    #os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = 'youtube'
    api_version = 'v3'
    client_secrets_file = os.path.join(here, 'client_secret.json')

    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    tokfile = os.path.join(here, 'token.pickle')
    if os.path.exists(tokfile):
        with open(tokfile, 'rb') as token:
            credentials = pickle.load(token, encoding='latin1')
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:# Get credentials and create an API client
          flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
          credentials = flow.run_console()
        # Save the credentials for the next run
        with open(tokfile, 'wb') as token:
          pickle.dump(credentials, token)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
          "snippet": {
            "categoryId": "22",
            "description": "Allsky camera timelapse",
            "title": title
          },
          "status": {
            "privacyStatus": "public"
          }
        },
        
        media_body=MediaFileUpload(fname,  chunksize=-1, resumable=True)
    )
    try: 
      status, response = request.next_chunk() # request.execute()
      print(status, response)
      if response is not None:
        if 'id' in response:
          print(f'Video id  {response["id"]} was successfully uploaded.')
          return True
        else:
          print(f'The upload failed with an unexpected response: {response}')
          return False
    except HttpError as e:
       print(f'HTTP error {e.resp.status} arose with message: {e.content}')
       return False


def updateCrontab(here, offset=30, lati=51.88, longi=-1.31, elev=80):
  batchname = 'youtubeUploader'
  obs = ephem.Observer()
  obs.lat = float(lati) / 57.3 # convert to radians, close enough for this
  obs.lon = float(longi) / 57.3
  obs.elev = float(elev)
  obs.horizon = -6.0 / 57.3 # degrees below horizon for darkness

  sun = ephem.Sun()
  rise = obs.next_rising(sun).datetime()
  starttime = rise + datetime.timedelta(minutes=-offset)
  print('Setting batch start time to', starttime.strftime('%H:%M'))

  cron = CronTab(user=True)
  for job in cron:
    if 'youtubeUploader.sh' in job.command:
        cron.remove(job)
        cron.write()
  job = cron.new(f'{here}/youtubeUploader.sh > /var/log/ytupload.log 2>&1')
  job.setall(starttime.minute, starttime.hour, '*', '*', '*')
  cron.write()
  return


def scanLogFile(logname, toddt):
  lis = open(logname,'r').readlines()
  tllines = [x for x in lis if 'Timelapse complete' in x]
  tllines = [x for x in tllines if toddt.strftime('%Y-%m-%d') in x]
  if len(tllines) > 0:
     return True
  return False

MINS = 5

if __name__ == "__main__":
  today = datetime.datetime.now()
  here = os.path.split(os.path.abspath(__file__))[0]
  logfile = sys.argv[1]
  allskyhome = sys.argv[2]
  yest = today + datetime.timedelta(days=-1)
  title = f'Allsky timelapse for {yest.strftime("%Y-%m-%d")}'
  fname = f'allsky-{yest.strftime("%Y%m%d")}.mp4'
  fname = os.path.join(allskyhome, 'images', f'{yest.strftime("%Y%m%d")}', fname)
  found = False
  counter = 0
  print(f'waiting for {fname}')
  while not found and counter < MINS*36:
    found = scanLogFile(logfile, today)
    if found:
      print(f'   uploading {fname}')
      uploadToYoutube(here, title, fname)
      break
    sleep(MINS*60)
  updateCrontab(here)