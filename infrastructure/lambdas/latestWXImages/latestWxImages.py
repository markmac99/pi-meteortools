# Copyright (C) Mark McIntyre
import boto3


def createLatest(buck, obj, outbuck):
    # don't want copies of the spectrogram or polar angle images
    if 'spectro' in obj or 'polar' in obj:
        return 
    elif 'therm' in obj:
        newn = 'satimgs/latest-therm.jpg'
    elif 'METEOR' in obj and 'rectified' in obj:
        newn = 'satimgs/latest-M2.jpg'
    else:
        newn = 'satimgs/latest' + obj[31:]
    print(newn)
    s3 = boto3.resource('s3')
    src = {'Bucket': buck, 'Key': obj}
    s3.meta.client.copy_object(Bucket=outbuck, Key=newn, CopySource=src)
    return 


if __name__ == '__main__':
    s3bucket = 'mjmm-data'
    outbucket = 'mjmm-data'
    s3object = 'satimgs/NOAA-19-20220910-094635-HVC.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/NOAA-19-20220910-094635-HVC-precip.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/NOAA-19-20220910-094635-MSA.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/NOAA-19-20220910-094635-MSA-precip.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/NOAA-19-20220910-094635-HVCT.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/NOAA-19-20220910-094635-HVCT-precip.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/NOAA-19-20220910-094635-MCIR.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/NOAA-19-20220910-094635-MCIR-precip.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/NOAA-19-20220910-094635-spectrogram.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/NOAA-19-20220910-094635-therm.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/NOAA-19-20220910-094635-polar-azel.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/NOAA-19-20220910-094635-polar-direction.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/METEOR-M-2-20220910-074036-polar-azel.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/METEOR-M-2-20220910-074036-polar-direction.jpg'
    createLatest(s3bucket, s3object, outbucket)
    s3object = 'satimgs/METEOR-M-2-20220910-074036-122-rectified.jpg'
    createLatest(s3bucket, s3object, outbucket)
    

def lambda_handler(event, context):
    record = event['Records'][0]
    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    outbucket = 'mjmm-data'
    if 'latest' not in s3object: 
        print('creating latest NOAA image')
        createLatest(s3bucket, s3object, outbucket)
