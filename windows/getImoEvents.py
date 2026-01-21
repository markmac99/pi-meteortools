# copyright Mark McIntyre, 2025-

import os
import sys
import pandas as pd
import requests
import datetime

MINMAG = -2
TIMERANGE = 15


def getTableData(yr, startmth=None, endmth=None):
    baseurl = f'https://fireballs.imo.net/members/imo_view/browse_events?country=235%7CUnited+Kingdom&year={yr}&num_report_select=&event=&event_id=&event_year=&num_report=5'
    res = requests.get(baseurl)
    if res.status_code != 200:
        print('unable to retrieve data')
        return None
    strdata = res.content.decode('utf-8')
    start = strdata.find('<table class=')
    end = strdata.find('/table')
    htmldata = strdata[start:end+7]
    splitrows = htmldata.split('<tr>')
    datarows = [r for r in splitrows if r[:10]=='<td class=']
    eventdata = []
    for thisrow in datarows:
        eles = thisrow.split('</td>')
        eventurl = 'https://fireballs.imo.net' + eles[0][eles[0].find('href')+5:eles[0].find(' title')].strip('"')
        eventdt = eles[2][eles[2].find('>')+1:]
        eventdt = datetime.datetime.strptime(eventdt,'%Y-%m-%d %H:%M UT')
        eventloc = eles[5][4:]
        eventdata.append([eventdt, eventloc, eventurl])
    df = pd.DataFrame(eventdata, columns=['evtdate','evturl','evtloc'])
    if startmth:
        df = df[df.evtdate >= datetime.datetime(yr,startmth,1)]
    if endmth:
        if endmth == 12:
            df = df[df.evtdate <= datetime.datetime(yr+1,1,1)]
        else:
            df = df[df.evtdate <= datetime.datetime(yr,endmth+1,1)]
    return df


def getMatchingUkmonEvents(yr, startmth, endmth):
    print('getting ukmon data')
    mthdata = pd.read_parquet(f'https://archive.ukmeteors.co.uk/browse/parquet/matches-full-{yr}.parquet.snap')
    mthdata = mthdata[mthdata._mag < MINMAG]
    mthdata = mthdata[mthdata._M_ut >= startmth]
    mthdata = mthdata[mthdata._M_ut <= endmth]
    copydata = mthdata[['_localtime','_mag','_amag','_stream','_lng1','_lat1','_vg','url']].copy()
    copydata['ts']=[datetime.datetime.strptime(x, '_%Y%m%d_%H%M%S') for x in copydata._localtime]
    copydata = copydata[copydata._mag < MINMAG]
    print(f'got {len(copydata)} rows')
    return copydata


if __name__ == '__main__':
    yr = int(sys.argv[1])
    smth = int(sys.argv[2])
    emth = int(sys.argv[3])
    fname = f'./events-{yr}-{smth}-{emth}.csv'
    if not os.path.isfile(fname):
        print('reading data from IMO')
        tbldata = getTableData(yr, smth, emth)
        tbldata.to_csv(fname)
    else:
        print('reading data from file')
        tbldata =pd.read_csv('c:/temp/events-2025-10-11.csv', index_col=0)
    mthdata = getMatchingUkmonEvents(yr, smth, emth)

    for _, rw in tbldata.iterrows():
        testdt = datetime.datetime.strptime(rw.evtdate, '%Y-%m-%d %H:%M:%S')
        fl1 = mthdata[mthdata.ts > testdt-datetime.timedelta(minutes=TIMERANGE)]
        fl2 = fl1[fl1.ts < testdt+datetime.timedelta(minutes=TIMERANGE)]
        if len(fl2) > 0:
            print('potential match')
            print(f'{rw.evtdate} {rw.evturl} {rw.evtloc}')
            for _, rw2 in fl2.iterrows():
                print(f'{rw2._localtime} {rw2._lat1} {rw2._lng1} {rw2._stream} {rw2._mag} {rw2.url}')
