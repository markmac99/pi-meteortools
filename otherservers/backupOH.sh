#!/bin/bash

# bash script to backup the openhab installation
# 
# crontab entry:
# 15 3 * * Sun $HOME/src/tackley-tools/backupOH.sh >> $HOME/logs/backup.log 2>&1

# openhab first
[ ! -d ~/backups/openhab ] && ln -s /var/lib/openhab/backups ~/backups/openhab
dom=$(date +%d)
if [ $dom -lt 8 ]; then 
    echo "full"
    sudo openhab-cli backup --full
else
    echo "incremental"
    sudo openhab-cli backup
fi 
cd $HOME/backups/openhab/
sudo find . -mtime +35 -exec rm -f {} \;

# then influxdb
mkdir -p $HOME/backups/influx/$(date +%Y%m%d)
influxd backup -portable $HOME/backups/influx/$(date +%Y%m%d)
cd $HOME/backups/influx/
find . -mtime +35 -exec rm -Rf {} \;

# then push to AWS for safekeeping
cd $HOME/backups
/usr/local/bin/aws s3 sync . s3://mjmm-website-backups/openhab/ --delete

echo "finished"
echo "========"
