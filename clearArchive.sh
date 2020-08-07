#!/bin/bash
# clear down anything older than 20 days from ArchivedFiles

cd /home/pi/RMS_data/ArchivedFiles
find . -maxdepth 1 -name "*.bz2" -type f -mtime +20 -exec rm -f {} \;
find . -maxdepth 1 -type d -mtime +20 -exec rm -Rf {} \;
