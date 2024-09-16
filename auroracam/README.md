# A Simple Aurora Camera

The scripts in this folder implement a very simple aurora camera using a barebones IP camera. Python 3.7 or later required. 

## How it works
A python script captures an image from the camera every few seconds. During the day it writes the image to $DATADIR/../live.jpg. At night it writes it to a datestamped directory. At the end of the night, the saved images are made into an MP4 and thhe host is rebooted to ensure a clean start for the next day. 
The software also captures during the day, creating a separate set of data and timelapse. 

### Scheduling the job
Each time the script is run it creates or updates a scheduled job in the Pi's crontab so there's no need to do this manually. 

### Uploads to S3
The images and MP4 can also be uploaded to an AWS S3 bucket by specifying an upload bucket in the config file.Images are uploaded every 30 seconds.  

### Configuration File
This holds the IP address, camera location and name, and the location of data and logs as well as the name of any S3 bucket if thats being used. You can also tweak the gain to set the camera to at night though the default should be good.  See the section on Installation for more information. 

### Camera Configuration
The camera is configured by the software (using the DVRIP library) and no manual tweaks should be needed. The exposure and gain are automatically changed at dawn and dusk. 

## Hardware

The camera module I'm using is an IMX307 but an IMX291 should also work.   
I'm running the software on an Intel ATOM Z8350 miniPC with 4GB memory running Armbian but it should work on pretty much any hardware. 

### Installation

On the target computer, run the following  

``` bash
wget https://raw.githubusercontent.com/markmac99/pi-meteortools/master/auroracam/install.sh
bash ./install.sh
```

* Now edit *config.ini* and fill in following
  * IPADDRESS - the IP address of your camera
  * CAMID - a camera ID which will be used as part of the filenames. 
  * LAT, LON, ALT - your latitude & longitude in degrees (+ for East) and elevation above sealevel in metres. 
  * other values can be left at their defauults. 
* uploading to AWS S3 or an FTP server
  * S3UPLOADLOC - if you want to upload to AWS S3 storage, provide a bucket name eg *s3://mybucket*. 
  * IDKEY - a CSV file containing the AWS key and secret.
* uploading to an FTP server
  * FTPSERVER, FTPUSER, FTPKEY - the server, userid and ssh keyfile to use
  * FTPUPLOADLOC - the folder on the server to upload to
  
Now run *startAuroraCam.sh* and it should complete the installation and start capturing data.

After the first few images have been captured, press Ctrl-C to abort, then reboot the Pi. Log in again and wait one minute, then you should find that the software has automatically started up and is saving images.

## webserver
A webserver is set up during installation and can be used to view the latest data, historical images and logs. 

## Data Archival
The process generates a lot of data and does not perform any housekeeping. You can use the script *archiveData.sh* to compress and delete data older than two weeks. 

If you have access to an sftp server you can also configure the system to upload tarballs of each night's data for safe keeping. You will need to add update the ARCHSERVER and ARCHFLDR values in the config file. You will also need to add an entry to `~/.ssh/config` with the security details, eg:  
``` bash
host myserver
    User someuser
    IdentityFile ~/.ssh/somekey
```