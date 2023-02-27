#!/bin/bash
# clear down anything older than 20 days from ArchivedFiles

cd /home/pi/RMS_data/ArchivedFiles
echo "clearing bz2 and ArchivedDir folders older than 20 days"
find . -maxdepth 1 -name "*.bz2" -type f -mtime +20 -exec rm -vf {} \;
find . -maxdepth 1 -type d -mtime +20 -exec rm -Rf {} \;

echo "clearing logs older than 10 days"
find /home/pi/RMS_data/logs -mtime +10 -exec rm -vf {} \;