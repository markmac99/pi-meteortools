PI Scripts
=========
This folder contains scripts for use on the Pi to monitor, maintain and analyse the
data from the RMS processes.

checkForMeteors.sh
------------------
Run this daily from a crontab to email yourself a daily report. 
Requires ssmtp which can be installed with 'sudo apt-get install -y ssmtp'
You will then need to configure ssmtp as explained in its documentation.

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
