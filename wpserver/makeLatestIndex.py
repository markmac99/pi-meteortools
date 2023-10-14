import boto3
import os
import datetime


def createLatestIndex():
    here = os.path.split(os.path.abspath(__file__))[0]
    sess = boto3.Session(profile_name='default')
    s3 = sess.resource('s3')
    buck = s3.Bucket('mjmm-data')

    templdata = open(os.path.join(here, 'latestindex.js'), 'r').read()
    offs = 1
    while 'TEMPLATE' in templdata:
        dtstr = (datetime.datetime.now() + datetime.timedelta(days=-offs)).strftime('%Y%m%d')
        #print(dtstr)
        uk06files =[os.key for os in buck.objects.filter(Prefix='UK0006') if dtstr in os.key] 
        #print(uk06files)
        if any('dailystacks' in s for s in uk06files) and 'UK0006STILLTEMPLATE' in templdata:
            templdata = templdata.replace('UK0006STILLTEMPLATE', [x for x in uk06files if 'dailystacks' in x][0])
        if any('trackstacks' in s for s in uk06files) and 'UK0006TRACKTEMPLATE' in templdata:
            templdata = templdata.replace('UK0006TRACKTEMPLATE', [x for x in uk06files if 'trackstacks' in x][0])
        if any('timelapse' in s for s in uk06files) and 'UK0006VIDEOTEMPLATE' in templdata:
            templdata = templdata.replace('UK0006VIDEOTEMPLATE', [x for x in uk06files if 'timelapse' in x][0])

        uk0ffiles =[os.key for os in buck.objects.filter(Prefix='UK000F') if dtstr in os.key] 
        if any('dailystacks' in s for s in uk0ffiles) and 'UK000FSTILLTEMPLATE' in templdata:
            templdata = templdata.replace('UK000FSTILLTEMPLATE', [x for x in uk0ffiles if 'dailystacks' in x][0])
        if any('trackstacks' in s for s in uk0ffiles) and 'UK000FTRACKTEMPLATE' in templdata:
            templdata = templdata.replace('UK000FTRACKTEMPLATE', [x for x in uk0ffiles if 'trackstacks' in x][0])
        if any('timelapse' in s for s in uk0ffiles) and 'UK000FVIDEOTEMPLATE' in templdata:
            templdata = templdata.replace('UK000FVIDEOTEMPLATE', [x for x in uk0ffiles if 'timelapse' in x][0])

        uk1lfiles =[os.key for os in buck.objects.filter(Prefix='UK001L') if dtstr in os.key] 
        if any('dailystacks' in s for s in uk1lfiles) and 'UK001LSTILLTEMPLATE' in templdata:
            templdata = templdata.replace('UK001LSTILLTEMPLATE', [x for x in uk1lfiles if 'dailystacks' in x][0])
        if any('trackstacks' in s for s in uk1lfiles) and 'UK001LTRACKTEMPLATE' in templdata:
            templdata = templdata.replace('UK001LTRACKTEMPLATE', [x for x in uk1lfiles if 'trackstacks' in x][0])
        if any('timelapse' in s for s in uk1lfiles) and 'UK001LVIDEOTEMPLATE' in templdata:
            templdata = templdata.replace('UK001LVIDEOTEMPLATE', [x for x in uk1lfiles if 'timelapse' in x][0])

        uk2ffiles =[os.key for os in buck.objects.filter(Prefix='UK002F') if dtstr in os.key] 
        if any('dailystacks' in s for s in uk2ffiles) and 'UK002FSTILLTEMPLATE' in templdata:
            templdata = templdata.replace('UK002FSTILLTEMPLATE', [x for x in uk2ffiles if 'dailystacks' in x][0])
        if any('trackstacks' in s for s in uk2ffiles) and 'UK002FTRACKTEMPLATE' in templdata:
            templdata = templdata.replace('UK002FTRACKTEMPLATE', [x for x in uk2ffiles if 'trackstacks' in x][0])
        if any('timelapse' in s for s in uk2ffiles) and 'UK002FVIDEOTEMPLATE' in templdata:
            templdata = templdata.replace('UK002FVIDEOTEMPLATE', [x for x in uk2ffiles if 'timelapse' in x][0])

        acmfiles = [os.key for os in buck.objects.filter(Prefix='UK9999') if dtstr in os.key] 
        acmnonday = [x for x in acmfiles if 'day' not in x]
        if 'AURCAMVIDEOTEMPLATE' in templdata and len(acmnonday) > 0:
            templdata = templdata.replace('AURCAMVIDEOTEMPLATE', acmnonday[0])

        askfiles = [os.key for os in buck.objects.filter(Prefix='allsky') if dtstr in os.key]
        asknonday = [x for x in askfiles if 'day' not in x]
        #print(asknonday)
        if any('startrails' in s for s in asknonday) and 'ALLSKYSTILLTEMPLATE' in templdata:
            templdata = templdata.replace('ALLSKYSTILLTEMPLATE', [x for x in asknonday if 'startrails' in x][0])
        if any('videos' in s for s in asknonday) and 'ALLSKYVIDEOTEMPLATE' in templdata:
            templdata = templdata.replace('ALLSKYVIDEOTEMPLATE', [x for x in asknonday if 'videos' in x][0])
        #print(templdata)
        if 'TEMPLATE' not in templdata:
            break
        offs = offs + 1
        #sleep(10000)
    currdt = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y%m%d')
    tmpdir = os.getenv('TMPDIR', default='/tmp')
    with open(os.path.join(tmpdir, f'latest_{currdt}.js'), 'w') as outf:
        outf.write(templdata)
    datadir = os.getenv('DATADIR', default='/tmp')
    targfile = os.path.join(datadir, 'latestindex.js')
    with open(targfile, 'w') as outf:
        outf.write(templdata)


if __name__ == '__main__':
    createLatestIndex()
