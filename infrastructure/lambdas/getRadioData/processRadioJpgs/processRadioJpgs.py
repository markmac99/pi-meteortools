import shutil
import tempfile
import boto3


# SpecLab is creating files called interesting_X.jpg. I want the most recent two 
# to display on the website. 
def updateInterestingJpgs(srcbucket, srckey):
    destbucket = 'mjmm-data'
    s3 = boto3.resource('s3')
    tmploc = tempfile.mkdtemp()
    # in the target bucket, copy screenshot1.jpg to screenshot2.jpg
    sc1key = 'Radio/screenshot1.jpg'
    sc2key = 'Radio/screenshot2.jpg'
    copysrc = {'Bucket': destbucket, 'Key': sc1key}
    extraargs = {'ContentType': 'image/jpeg'}
    try:
        s3.meta.client.copy(copysrc, destbucket, sc2key, ExtraArgs=extraargs)
        print(f'uploaded {copysrc} to {destbucket}/{sc1key}')
    except:
        print('screenshot1.jpg not found')

    # then copy the new file to screenshot1.jpg
    copysrc = {'Bucket': srcbucket, 'Key': srckey}
    extraargs = {'ContentType': 'text/javascript'}
    s3.meta.client.copy(copysrc, destbucket, sc1key, ExtraArgs=extraargs)
    shutil.rmtree(tmploc)


if __name__ == '__main__':
    s3bucket='mjmm-rawradiodata'
    s3key = 'raw/interesting_24.jpg'
    updateInterestingJpgs(s3bucket, s3key)


def lambda_handler(event, context):
    record = event['Records'][0]
    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    updateInterestingJpgs(s3bucket, s3object)
    return
