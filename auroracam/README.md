# A Simple Aurora Camera

The scripts in this folder implement a very simple aurora camera using a barebones IP camera. Python 3.7 or later required. 

## How it works
A python script captures an image from the camera every few seconds. During the day it writes the image to $DATADIR/../live.jpg. At night it writes it to a datestamped directory. At the end of the night, the saved images are made into an MP4 and thhe host is rebooted to ensure a clean start for the next day. 

### Scheduling the job
Each time the script is run, it creates or updates a scheduled job in the Pi's crontab so there's no need to do this manually. 

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
<pre>
sudo apt-get install python3-opencv 
virtualenv ~/vAuroracam  
source ~/vAuroracam/bin/activate  
pip install --upgrade pip
pip install python-dvr python-crontab boto3 opencv-python ephem pillow MeteorTools
mkdir -p ~/source/auroracam
cd ~/source/auroracam
flist=(uploadLiveJpg.sh archiveData.sh grabImage.py config.ini ../pi/setExpo.py)
for f in ${flist[@]} ; do
wget https://raw.githubusercontent.com/markmac99/pi-meteortools/master/auroracam/${f}  
done 
chmod +x *.sh
</pre>
* Now edit *config.ini* and fill in following
    * IPADDRESS - the IP address of your camera
    * DATADIR, LOGDIR - locations on the Pi where logfiles should be written and a location on the Pi where data files should be written. I suggest something like *~/data/logs* and *~/data/auroracam*
    * CAMID - a camera ID which will be used as part of the filenames. 
    * LAT, LON, ALT - your latitude & longitude in degrees (+ for East) and elevation above sealevel in metres. 
    * UPLOADLOC - if you want to upload to AWS S3 storage, provide a bucket name eg *s3://mybucket*. You'll have to configure AWS connectivity yourself. 
  
Now run *uploadLiveJpg.sh* and it should start capture.  
 
**Note that this is a commandline tool - do not close the terminal window that it is running in or the programme will stop.**

## Data Archival
The process generates a lot of data and does not perform any housekeeping. You can use the script *archiveData.sh* to compress and delete data older than two weeks. 