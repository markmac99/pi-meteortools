# README for radio tools

This folder contains tools to augment R Bassom's python-based radio meteor detection software.

* `meteorradio.service` runs Richard's meteorradio.py as a Service. This allows the OS to handle stops and restarts automatically. 
* `meteorradio.sh` is used by the service and reads the software's settings from...
* `config.ini` provides configuration settings for the software. 
* `installservice.sh` installs and starts the meteorradio service in user-space. 

Additional files manage data uploads to my website and dashboard:
* `monitorForNew.sh` monitors the meteorradio logfile for keywords that indicate a detection took place, * and then triggers an upload to my website. This script is run from cron as shown below. 
* `postStatsToMQ.sh` posts some statistics to my MQTT server every few minutes. Run from cron. 
* `updateRmobFiles.sh` creates RMOB compatible data files every few minutes. Run from cron. 

The crontab entries for htese tools are:
``` bash
*/5 * * * * $HOME/source/radiometeor_tackley/postStatsToMQ.sh > /dev/null 2>&1
@reboot  /usr/bin/sleep 20 && $HOME/source/radiometeor_tackley/monitorForNew.sh >> $HOME/radar_data/Logs/monitor-`date +\%Y-\%m-\%d`.log 2>&1
*/5 * * * * $HOME/source/radiometeor_tackley/updateRmobFiles.sh >> $HOME/radar_data/Logs/updateRmobFiles-`date +\%Y-\%m-\%d`.log 2>&1
```