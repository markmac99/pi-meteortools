A Simple Aurora Camera
======================

The scripts in this folder implement a very simple aurora camera, using a barebones IP camera.

A cron job starts the script uploadLiveJpg.sh 60 seconds after boot. This calls 
grabImage.py which captures an image from the camera every few seconds. During the day it writes
the image to $DATADIR/../live.jpg. At night it writes it to a datestamped directory.
The images are also uploaded in near-realtime to my website hosted on AWS. 

At the end of the night, the saved images are made into an MP4 which is also uploaded to my site. The computer is then rebooted to ensure a clean start for the next day. 

The camera is switched from day to night mode, and vice-versa, using the DVRIP library. 

Two support scripts are also present  
* archiveData.sh archives and then deletes older data to save space
* checkAuroracam.sh monitors the live image and if it becomes stale, reboots the computer. 

Key parameters such as IP address, location of data and logs, and gain to set the camera to at
night, are read from config.ini