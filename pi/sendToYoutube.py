# -*- coding: utf-8 -*-
# Simple script to upload a video to Youtube
# Takes two arguments - title and filename
#
# REQUIRES:google-api-python-client google-auth-httplib2 google-auth-oauthlib
# Install these with pip in the usual way. 
# 
# NOTES:
#    To test this code, you must run it locally using your own API credentials.
#    See: https://developers.google.com/explorer-help/guides/code_samples#python

import os
import sys
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

scopes = ["https://www.googleapis.com/auth/youtube.upload"]


def main(title, fname):
    api_service_name = "youtube"
    api_version = "v3"

    local_path =os.path.dirname(os.path.abspath(__file__))

    # When you authenticate as explained in the API docs, you will be given a 
    # token in JSON form. Store the token in this file in the same folder as
    # this script 
    client_secrets_file = local_path + "/client_secret.json"

    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    pickle_file=local_path +'/token.pickle'
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            if sys.version_info.major < 3:
                credentials = pickle.load(token)
            else:
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
        with open(pickle_file, 'wb') as token:
            pickle.dump(credentials, token)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "categoryId": "22",
                "description": title,
                "title": title
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        
        media_body=MediaFileUpload(fname, chunksize=-1, resumable=True)
    )
    try: 
        status, response = request.next_chunk() # request.execute()
        print(status, response)
        if response is not None:
            if 'id' in response:
                print("Video id '%s' was successfully uploaded." % response['id'])
            else:
                exit("The upload failed with an unexpected response: %s" % response)
    except HttpError as e:
        error='HTTP error %d arose with status: \'%s\' ' % (e.resp.status, e.content)
        print(error)


if __name__ == "__main__":
    # Parameters: title to use and the file to upload
    title=sys.argv[1]
    fname=sys.argv[2]
    main(title, fname)
