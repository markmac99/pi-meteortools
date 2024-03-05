#
# Function to save an FTPdetect file and platepar as ECSV files
# Copyright (C) 2018-2023 Mark McIntyre
#
import os
import boto3


def updateSaveFile(dtstr):
    srcbucket = os.getenv('ACBUCKET', default='mjmm-data')
    srcfldr = os.getenv('ACFOLDER', default='auroracam')
    acfile ='FILES_TO_UPLOAD.inf'
    s3 = boto3.client('s3')
    srcfname = f'{srcfldr}/{acfile}'
    locfname = f'/tmp/{acfile}'
    try:
        s3.download_file(srcbucket, srcfname, locfname)
    except Exception:
        ff = open(locfname, 'w')
        ff.close()
    lis = open(locfname, 'r').readlines()
    lis.append(dtstr + '\n')
    open(locfname, 'w').writelines(lis)
    s3.upload_file(locfname, srcbucket, srcfname)
    return 'ok'


def lambda_handler(event, context):
    qs = event['queryStringParameters']
    if qs is not None:
        if 'dt' in qs:
            dt = qs['dt']
            res = updateSaveFile(dt)
            return {
                'statusCode': 200,
                'body': res
            }
    else:
        return {
            'statusCode': 200,
            'body': "usage: saveacapi?dt=YYYYmmdd_HHMMSS"
        }
