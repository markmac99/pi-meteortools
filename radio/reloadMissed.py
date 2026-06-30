# copyright Mark McIntyre, 2026-

# python script to insert missing radio hourly and daily data, if i have it

import os
import sys
import requests
from requests.auth import HTTPBasicAuth 
import pandas as pd
import datetime


def getInfluxUrl():
    passwordfile = os.path.expanduser('~/.ssh/influxdb')
    with open(passwordfile) as inf:
        usr = inf.readline().strip()
        pwd = inf.readline().strip()    
    influxserver = 'ohserver'
    influxport = 8086
    influxdatabase = 'openhab'
    influxurl = f'http://{influxserver}:{influxport}/write?db={influxdatabase}'
    return influxurl, usr, pwd, influxserver, influxport, influxdatabase


def convertToIdbFmt(df, meas, outdir):
    df['ts1'] = [int(x.timestamp()*1e9) for x in df.ts]
    # print(df.columns)
    with open(os.path.join(outdir, f'{meas}.txt'), 'w', newline='\n') as outf:
        for _, rw in df.iterrows():
            outf.write(f'{rw.measurement} value={rw.value} {rw.ts1}\n')
    idbdata = open(os.path.join(outdir, f'{meas}.txt'), 'rb').read()
    return idbdata
    

def updateInfluxDB(df, meas, outdir):
    url, usr, pwd, _, _, _ = getInfluxUrl()
    idbdata = convertToIdbFmt(df, meas, outdir=outdir)
    # curl -i -XPOST -u $influxuser:$influxpw "http://$influxserver:$influxport/write?db=$influxdatbase" --data-binary @$i
    authn = HTTPBasicAuth(usr, pwd)
    requests.post(url, data=idbdata, auth=authn)
    return len(df)

def loadRawData(srcfile, st=None, et=None):

    df1 = pd.read_csv(srcfile)
    df1.drop(columns=['user_ID','signal','noise','frequency','lat','long','source','timesync','snratio','doppler_estimate', 'durationc','durations'], inplace=True)
    df1['ts'] = [datetime.datetime.strptime(f'{d} {t}','%Y-%m-%d %H:%M:%S.%f') for d,t in zip(df1.date, df1.time)] 

    daydf = pd.DataFrame()
    daydf['ts'] = df1.ts
    daydf['measurement'] = ['radiopi_daily'] * len(daydf)
    daydf['value'] = [1]*len(daydf)

    hourdf = pd.DataFrame()
    hourdf['ts'] = df1.ts
    hourdf['measurement'] = ['radiopi_hourly'] * len(hourdf)
    hourdf['value'] = [1]*len(hourdf)

    dayct = 0
    hourct = 0
    start_day = df1.iloc[0].ts.day
    start_hr = df1.iloc[0].ts.hour

    for _, rw in df1.iterrows():
        if rw.ts.day != start_day:
            dayct = 1
            start_day = rw.ts.day
        else:
            dayct += 1
            idx = daydf[daydf.ts == rw.ts].index
            daydf.loc[idx, 'value'] = dayct
        if rw.ts.hour != start_hr:
            hourct = 1
            start_hr = rw.ts.hour
        else:
            hourct += 1
            idx = hourdf[hourdf.ts == rw.ts].index
            hourdf.loc[idx, 'value'] = hourct

    if st:
        daydf = daydf[daydf.ts >= st]
        hourdf = hourdf[hourdf.ts >= st]
    if et:
        daydf = daydf[daydf.ts <= et]
        hourdf = hourdf[hourdf.ts <= et]

    return daydf, hourdf


if __name__ == '__main__':
    srcdata = sys.argv[1]
    sd = None
    ed = None
    if len(sys.argv) > 2:
        dt_beg = sys.argv[2]
        sd = datetime.datetime.strptime(dt_beg,'%Y-%m-%dT%H:%M:%SZ')
    if len(sys.argv) > 3:
        dt_end = sys.argv[3]
        ed = datetime.datetime.strptime(dt_end,'%Y-%m-%dT%H:%M:%SZ')

    daydf, hrdf = loadRawData(srcdata, sd, ed)

    updateInfluxDB(daydf, 'radiopi_daily', '.')
    updateInfluxDB(hrdf, 'radiopi_hourly', '.')
