PI Scripts
=========
This folder contains scripts for use on the Pi to monitor, maintain and analyse the
data from the RMS processes.

installUkMonlive.sh
-------------------
A script that will upload meteor events to UKMON Live. See documentation in the 
Releases section for installation instructions, but in short, copy the file to your Pi,
make it executable and then run it. NB: you must set the auto-reboot flag in RMS's 
.config file so that the live uploader can track the correct log file. 

installUkMonarch.sh
-------------------
A script that sends data to the UKMON Archive. See documentation in the 
Releases section for installation instructions, but in short, copy the file to your Pi,
make it executable and then run it. It will self-install and then send files to ukmon every day at 11am.

checkForMeteors.sh
------------------
Run this daily from a crontab to email yourself a daily report. 
Requires ssmtp which can be installed with 'sudo apt-get install -y ssmtp'
You will then need to configure ssmtp as explained in its documentation. Email 
details are picked up from config.ini (see below)

postProcess.sh
--------------
Run this daily from a crontab to execute a few python processes to update the
stack of the night's event, create JPGs from each FF file, create a timelapse of 
the whole night and optionally upload the timelapse to youtube, if you have a 
channel. 
There is also a function to create short MP4 videos from each meteor. This is
not yet integrated into RMS and so is commmented out for now. 

sendToYoutube.py
----------------
Uses the Google APIs to send the all-night timelapse to your youtube channel, if 
you have one and configure it correctly. An explanation of how to configure this
is covered in the Google API docs. 

sample-crontab.txt
------------------
example showing the lines you might want to add to crontab to execute the scripts
on a daily basis. 

config.ini
----------
Contains a few variables used by the other scripts. Update this according to your
needs. 

