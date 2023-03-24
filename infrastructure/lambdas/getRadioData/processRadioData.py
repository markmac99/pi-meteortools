# Copyright (C) Mark McIntyre
import numpy as np
import boto3
import matplotlib
import matplotlib.pyplot as plt
import calendar
import csv
import os
import shutil
import configparser as cfg
import tempfile
import datetime
#from matplotlib.ticker import MultipleLocator

interval = 100  # millisecs between loops in Colorlab


def ConvertToCsv(yr, mth, dy, tmpfldr):
    print('converting to CSV for ' + yr + mth + dy)
    # dt = "{:4d}{:02d}{:02d}".format(yr,mt,dy)
    dt = yr + mth # + dy

    config = cfg.ConfigParser()
    config.read(os.path.join(tmpfldr,'radiostation.ini'))
    lat = float(config['observer']['Lati'])
    lng = float(config['observer']['Lati'])
    id = config['observer']['station']
    alt = float(config['observer']['altitude'])
    tz = int(config['observer']['tz'])

    srcfile = os.path.join(tmpfldr, 'event_log_' + dt + '.csv')

    targfile = os.path.join(tmpfldr, 'R' + yr + mth + dy + '_' + id + '.csv')

    outf = open(targfile, 'w+')

    with open(srcfile) as inf:
        outf.write('Ver,Y,M,D,h,m,s,Bri,Dur,freq,ID,Long,Lat,Alt,Tz\n')
        mydata = csv.reader(inf, delimiter=',')
        for row in mydata:
            dstamp=row[0]
            fdy = dstamp[8:10]
            if fdy == dy: 
                tstamp = row[1]
                hr = tstamp[0:2]
                mi = tstamp[3:5]
                se = tstamp[6:9]
                bri = round(float(row[2]) - float(row[3]), 2)
                freq = row[6]
                dur = float(row[7]) * interval
                s = "RMOB,{:s},{:s},{:s},{:s},{:s},{:s},".format(yr, mth, dy, hr, mi, se)
                s = s + "{:f},{:f},{:s},".format(bri, dur, freq)
                s = s + "{:s},{:f},{:f},{:f},{:d}\n".format(id, lng, lat, alt, tz)
                outf.write(s)
    outf.close

    return targfile


def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", cbaron=1, **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    cbaron
        Whether or not to display the cbar
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    if cbaron == 1:
        cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
        cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="top", labelpad=5)
    else:
        cbar = None

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    # for edge, spine in ax.spines.items():
    #    spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1] + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0] + 1) - 0.5, minor=True)
    # ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "white"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A list or array of two color specifications.  The first is used for
        values below a threshold, the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max()) / 2.0

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts


def readRMOBFile(rmobfile):
    _, rmobname = os.path.split(rmobfile)
    spls = rmobname.split('-')
    tod = spls[1]
    tod = tod[:6]
    mthdays = calendar.monthrange(int(tod[:4]), int(tod[4:6]))[1]
    myarray = np.zeros((24, mthdays), dtype=int)
    with open(rmobfile) as myfile:
        mydata = csv.reader(myfile, delimiter=',')
        line_count = 0
        for row in mydata:
            if len(row) <1:
                continue
            yr = row[0]
            ym = yr[0:6]
            dy = int(yr[6:8])
            hr = int(row[1])
            val = int(row[2])
            myarray[hr, dy - 1] = val
            line_count += 1
        print(f'Processed {line_count} lines.')
    cnts = myarray[:, dy - 1]
    dys = "{:02d}".format(dy)

    return myarray, cnts, dys, ym, mthdays


def readEventLogFile(evtfile, coloffset=0, inparray=None):
    _, evtname = os.path.split(evtfile)
    spls = evtname.split('_')
    tod = spls[2]
    tod = tod[:6]
    mthdays = calendar.monthrange(int(tod[:4]), int(tod[4:6]))[1]
    if inparray is None:
        myarray = np.zeros((24, mthdays), dtype=int)
    else:
        myarray = inparray
    with open(evtfile) as myfile:
        mydata = csv.reader(myfile, delimiter=',')
        line_count = 0
        for row in mydata:
            if len(row) <1:
                continue
            ymd = datetime.datetime.strptime(row[0], '%Y/%m/%d')
            ym = ymd.strftime('%Y%m')
            hms = row[1]
            hr = int(hms[:2])
            myarray[hr, ymd.day - 1 + coloffset] = myarray[hr, ymd.day - 1 + coloffset] +1
            line_count += 1
        print(f'Processed {line_count} lines.')
    cnts = myarray[:, ymd.day - 1 + coloffset]
    dys = "{:02d}".format(ymd.day)

    return myarray, cnts, dys, ym, mthdays


def makeColorGram(srcbucket, srckey):
    s3 = boto3.resource('s3')

    tmpfldr = tempfile.mkdtemp()
    # download the config file
    cfgfile = os.path.join(tmpfldr, 'radiostation.ini')
    s3.meta.client.download_file(srcbucket, 'radiostation.ini', cfgfile)

    # download the event-log files
    srcfldr, evtlogname = os.path.split(srckey)
    evtlog = os.path.join(tmpfldr, evtlogname)
    print(f'retrieving {srckey}')
    s3.meta.client.download_file(srcbucket, srckey, evtlog)

    spls = evtlogname.split('_')
    thisdt = spls[2]
    evtdt = datetime.datetime.strptime(thisdt,'%Y%m.csv')
    back1 = (evtdt + datetime.timedelta(days=-25)).strftime('%Y%m')
    back2 = (evtdt + datetime.timedelta(days=-55)).strftime('%Y%m')

    bmth0 = evtdt.strftime('%b')
    bmth1 = (evtdt + datetime.timedelta(days=-25)).strftime('%b')
    bmth2 = (evtdt + datetime.timedelta(days=-55)).strftime('%b')

    key = f'{srcfldr}/event_log_{back1}.csv'
    locback1 = f'{tmpfldr}/event_log_{back1}.csv'
    s3.meta.client.download_file(srcbucket, key, locback1)

    key = f'{srcfldr}/event_log_{back2}.csv'
    locback2 = f'{tmpfldr}/event_log_{back2}.csv'
    s3.meta.client.download_file(srcbucket, key, locback2)

    hrs = range(1, 25)
    # create heatmap for this month
    # named yyyymm.jpg eg 200206.jpg

    # read the event log file
    myarray, cnts, dom, ym, mthdays = readEventLogFile(evtlog)

    # labels for axes
    col_lbl = ["0", "", "", "3", "", "", "6", "", "", "9", "", "", "12",
        "", "", "15", "", "", "18", "", "", "21", "", ""]
    if mthdays == 31:
        row_lbl = ["1", "", "", "", "5", "", "", "", "", "10",
            "", "", "", "", "15", "", "", "", "", "20", "", "",
            "", "", "25", "", "", "", "", "30", ""]
    elif mthdays == 30:
        row_lbl = ["1", "", "", "", "5", "", "", "", "", "10",
            "", "", "", "", "15", "", "", "", "", "20", "", "",
            "", "", "25", "", "", "", "", "30"]
    elif mthdays == 29:
        row_lbl = ["1", "", "", "", "5", "", "", "", "", "10",
            "", "", "", "", "15", "", "", "", "", "20", "", "",
            "", "", "25", "", "", "", ""]
    else:
        row_lbl = ["1", "", "", "", "5", "", "", "", "", "10",
            "", "", "", "", "15", "", "", "", "", "20", "", "",
            "", "", "25", "", "", ""]

    # generate  heatmap
    #
    fig, ax = plt.subplots()
    im, _ = heatmap(myarray, col_lbl, row_lbl,
                    cmap="jet", cbarlabel="Meteors/hour")
    _ = annotate_heatmap(im, valfmt=" {x:.0f} ", fontsize=8, threshold=myarray.max() * 3 / 4)
    fig.tight_layout()

    plt.ylabel('Hour', labelpad=-2)

    plt.text(0.5, 1.1, f'Heatmap for {ym}', horizontalalignment='center', transform=ax.transAxes, fontsize=15)
    plt.xlabel('Day of Month')
    plt.tight_layout()

    heatmapname = os.path.join(tmpfldr, f'{ym}.jpg')
    plt.savefig(heatmapname, dpi=600, bbox_inches='tight')
    plt.close()

    # now generate the text and bar graph for today
    # as per the RMOB graphs
    # named yyyymmdd.jpg eg 20201225.jpg
    #
    matplotlib.pyplot.bar(x=hrs, height=cnts)
    plt.ylabel('Count')

    config = cfg.ConfigParser()
    config.read(cfgfile)
    lati = float(config['observer']['Lati'])
    longi = float(config['observer']['Longi'])
    if longi < 0:
        ew = " West"
        longi = longi * -1
    else:
        ew = " East"
    mins = int(6000 * (longi - int(longi)))
    longis = '{:03d}°{:04d}{:s}'.format(int(longi), mins, ew)
    if lati < 0:
        ns = " South"
        lati = longi * -1
    else:
        ns = " North"
    mins = int(6000 * (lati - int(lati)))
    latis = '{:03d}°{:04d}{:s}'.format(int(lati), mins, ns)

    obs = "Observer:      " + config['observer']['observer']
    loc1 = "    Location:    " + longis + " "
    cntr = "Country:        " + config['observer']['Country'] + "  "
    loc2 = "                    " + latis
    city = "City:              " + config['observer']['Country'] + "                 "
    freq = " Frequency: " + config['detector']['Freq']
    antn = "Antenna:       " + config['detector']['Antenna'] + "             "
    azim = "     Az: " + config['detector']['Azim'] + "° El: " + config['detector']['Elev'] + "°               "
    rfpr = "RF Preamp:   " + config['detector']['RFPreAmp'] + "             "
    recv = "        Reciever:    " + config['detector']['Reciever']
    obsm = "Obs Method: " + config['detector']['ObsMethod']
    comp = "Computer:    " + config['detector']['Computer']
    stat = config['observer']['Station']
    plt.title(f'{obs:<30}{loc1:<30}\n{cntr:<30}{loc2:<30}\n{city:<30}{freq:<30}\n'
        + f'{antn:<30}{azim:<30}\n{rfpr:<30}{recv:<30}\n{obsm:<60}\n{comp:<60}\n\n'
        + stat + ' Meteor Station\nCount of detections per hour ' + ym
        + '-' + dom, loc='left')

    plt.tight_layout()

    barchartfile = os.path.join(tmpfldr, f'{ym}{dom}.jpg')
    plt.savefig(barchartfile, dpi=600, bbox_inches='tight')
    plt.close()

    # create a single image combining the above two side by side
    # again as per the RMOB data
    # named RMOB_yyyymm.jpg

    ax = plt.subplot(1, 2, 2)
    img1 = plt.imread(heatmapname)
    plt.axis('off')
    plt.imshow(img1)
    ax = plt.subplot(1, 2, 1)
    img2 = plt.imread(barchartfile)
    plt.axis('off')
    plt.imshow(img2)

    # save this as RMOB_yyyymmdd.jpg
    #
    rmoblatestfile = os.path.join(tmpfldr, 'RMOB_latest.jpg')
    plt.savefig(rmoblatestfile, dpi=600, bbox_inches='tight')
    plt.close()

    # generate three-month heatmap
    mthdays = calendar.monthrange(int(thisdt[:4]), int(thisdt[4:6]))[1]
    m2 = calendar.monthrange(int(back1[:4]), int(back1[4:6]))[1]
    m3 = calendar.monthrange(int(back2[:4]), int(back2[4:6]))[1]
    mthdays = mthdays + m2 + m3
    myarray = np.zeros((24, mthdays), dtype=int)

    # read in three months of data
    #
    myarray, _, _, _, _ = readEventLogFile(locback2, 0, myarray)
    myarray, _, _, _, _ = readEventLogFile(locback1, m3, myarray)
    myarray, _, _, _, _ = readEventLogFile(evtlog, m2 + m3, myarray)

    fig, ax = plt.subplots()

    row_lbl = ["" for x in range(mthdays)]
    for i in range(mthdays):
        if not (i % 10):
            if i >= (m3 + m2):
                row_lbl[i] = bmth0 + '\n' + str(i - m2 - m3 + 1)
            elif i >= m3:
                row_lbl[i] = bmth1 + '\n' + str(i - m3 + 1)
            else:
                row_lbl[i] = bmth2 + '\n' + str(i + 1)

    im, _ = heatmap(myarray, col_lbl, row_lbl,
                    cmap="jet", cbaron=0, cbarlabel="Meteors/hour")
    fig.tight_layout()

    plt.ylabel('Hour', labelpad=-2)
    plt.text = ""
    plt.xlabel('Day of Month')
    #_, ax = plt.subplots()
    #ax.xaxis.set_major_locator(MultipleLocator(10))
    plt.tight_layout()

    threemthfile = os.path.join(tmpfldr, '3months_latest.jpg')
    plt.savefig(threemthfile, dpi=600, bbox_inches='tight')
    plt.close()

    # now make the CSV files
    csvfile = ConvertToCsv(thisdt[:4], thisdt[4:6], dom, tmpfldr)
    return s3, heatmapname, rmoblatestfile, threemthfile, csvfile, tmpfldr


def uploadFiles(s3, heatmapname, rmoblatestfile, threemthfile, csvfile):
    targbucket = 'mjmm-data'
    targfldr = 'Radio/'
    extraargs = {'ContentType': 'image/jpeg'}

    # now upload the heatmap to Radio/yyyy/yyyymm.jpg
    _, fname = os.path.split(heatmapname)
    curryr = fname[:4]
    key = targfldr + curryr + '/' + fname
    print(f'uploading to {key}')
    s3.meta.client.upload_file(heatmapname, targbucket, key, ExtraArgs=extraargs) 

    # full barchart plus heatmap
    _, fname = os.path.split(rmoblatestfile)
    key = targfldr + fname
    print(f'uploading to {key}')
    s3.meta.client.upload_file(rmoblatestfile, targbucket, key, ExtraArgs=extraargs) 

    # now 3 month heatmap
    _, fname = os.path.split(threemthfile)
    key = targfldr + fname
    print(f'uploading to {key}')
    s3.meta.client.upload_file(threemthfile, targbucket, key, ExtraArgs=extraargs) 

    # now upload the CSV file
    _, fname = os.path.split(csvfile)
    ymd=fname[1:9]
    targkey = targfldr + ymd[:4] + '/' + ymd[:6] + '/' + fname
    print(f'uploading to {targkey}')
    extraargs = {'ContentType': 'text/csv'}
    s3.meta.client.upload_file(csvfile, targbucket, targkey, ExtraArgs=extraargs) 

    # and then upload it to the ukmon-shared bucket too, using suitable creds
    sts_client = boto3.client('sts')

    try: 
        assumed_role_object=sts_client.assume_role(
            RoleArn="arn:aws:iam::822069317839:role/service-role/S3FullAccess",
            RoleSessionName="AssumeRoleSession1")
        credentials=assumed_role_object['Credentials']
        s3u = boto3.resource('s3',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
        print('about to push file')
        targkey =f'archive/Tackley/Radio/{ymd[:4]}/{ymd[:6]}/{fname}'
        s3u.meta.client.upload_file(csvfile, 'ukmon-shared', targkey, ExtraArgs=extraargs) 
    except: 
        print('unable to assume role')

    return 


if __name__ == '__main__':
    s3bucket = 'mjmm-rawradiodata'
    s3object = 'raw/event_log_202209.csv'
    print('calling makeColorGram')
    s3, heatmapname, rmoblatestfile, threemthfile, csvfile, tmpfldr = makeColorGram(s3bucket, s3object)
    #uploadFiles(s3, heatmapname, rmoblatestfile, threemthfile, csvfile)
    print(f'files stored in {tmpfldr}')


def lambda_handler(event, context):
    record = event['Records'][0]
    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']

    s3, heatmapname, rmoblatestfile, threemthfile, csvfile, tmpfldr = makeColorGram(s3bucket, s3object)
    uploadFiles(s3, heatmapname, rmoblatestfile, threemthfile, csvfile)
    shutil.rmtree(tmpfldr)
            
