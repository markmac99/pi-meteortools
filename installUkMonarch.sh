#!/bin/bash

echo "This script will install the UKMON ARCHIVE software"
echo "on your Pi. If you don't want to continue press Ctrl-C now"
echo " "
echo "You will need the location code, access key and secret provided by UKMON"
echo "If you don't have these press crtl-c and come back after getting them".
echo "nb: its best to copy/paste the keys from email to avoid typos."
echo " " 

read -p "continue? " yn
if [ $yn == "n" ] ; then
  exit 0
fi

echo "Installing the AWS CLI...."
sudo apt-get install -y awscli

mkdir ~/ukmon
echo "Installing the package...."
ARCHIVE=`awk '/^__ARCHIVE_BELOW__/ {print NR + 1; exit 0; }' $0`
tail -n+$ARCHIVE $0 | tar xzv -C ~/ukmon

CREDFILE=~/ukmon/.archcreds

if [ -f $CREDFILE ] ; then
  read -p "Credentials already exist; overwrite? (yn) " yn
  if [[ "$yn" == "y" || "$yn" == "Y" ]] ; then 
    redocreds=1
  else
    redocreds=0
  fi
else
  redocreds=1
fi

if [ $redocreds -eq 1 ] ; then 
  while true; do
    read -p "Location: " loc
    read -p "Access Key: " key
    read -p "Secret: " sec 
    echo "you entered: "
    echo $loc
    echo $key
    echo $sec
    read -p " is this correct? (yn) " yn
    if [[ "$yn" == "y" || "$yn" == "Y" ]] ; then 
      break 
    fi
  done 
    
  echo "Creating credentials...."
  echo "export AWS_ACCESS_KEY_ID=$key" > $CREDFILE
  echo "export AWS_SECRET_ACCESS_KEY=$sec" >> $CREDFILE
  if [ "ARCHIVE" == "ARCHIVE" ] ; then 
    echo "export AWS_DEFAULT_REGION=eu-west-2" >> $CREDFILE
  else
    echo "export AWS_DEFAULT_REGION=eu-west-1" >> $CREDFILE
  fi
  echo "export loc=$loc" >> $CREDFILE
  chmod 0600 $CREDFILE
fi 
echo "Scheduling job..."
if [ "ARCHIVE" == "ARCHIVE" ] ; then 
  crontab -l | grep archToUKmon.sh
  if [ $? == 1 ] ; then
    crontab -l > /tmp/tmpct
    echo "0 11 * * * /home/pi/ukmon/archToUkMon.sh >> /home/pi/ukmon/archiver.log 2>&1" >> /tmp/tmpct
    crontab /tmp/tmpct
    \rm -f /tmp/tmpct
  fi 
else
  crontab -l | grep liveMonitor.sh > /dev/null
  if [ $? == 1 ] ; then
    crontab -l > /tmp/tmpct
    echo "@reboot sleep 3600 && /home/pi/ukmon/liveMonitor.sh >> /home/pi/ukmon/monitor.log 2>&1" >> /tmp/tmpct
    crontab /tmp/tmpct
    \rm -f /tmp/tmpct
  fi 
fi
echo ""
echo "done"
exit 0

__ARCHIVE_BELOW__
� �^ ��[o� p?�)�2K�*��4Ҧ<�eo}�婪j$fq�28mv��=Y�]��{��i�'٘�� T��w���<�il�'1C������|�s{$eQf�<[�UUr�a�*f̞�w~5Ĥz��s���S��z�L��+��k_Ű�/�
φ��e�F�2��9{eTR�p{k^��F�a���V�%�Z�S3�v���&@n<zH�\_cj�CaQ�C�=L�����d���f]j�y����"?�xak�`�ԙe}���/�C�Nu��X>��-�|�z����I��.. ?��&���Kx	������x���o��n�yln�PwcD�K��ncar:�����i�7�ʇ���U;���xZ7~Q�I�ʮ�&̶��ھm��q~)�	x7��֎��#M!�B!�B!�B!�B��3,)� (  