#!/bin/bash

if [ $# < 2] ; then
    echo "Usage: ./updateKeys LIVE|ARCHIVE"
    echo "Specify LIVE or ARCHIVE as required"
fi 
echo "This script will replace your $1 uploader access keys."
read -p "Do you want to continue? " yn
if [ $yn == "n" ] ; then
  exit 0
fi
if [ "$1" == "LIVE" ] ; then
    CREDFILE=/home/pi/ukmon/.livecreds
else
    CREDFILE=/home/pi/ukmon/.archcreds
fi 

cp $CREDFILE $CREDFILE.bak
source $CREDFILE
echo "Please enter the keys sent to you by email, short key first."
read -p "Access Key: " key
read -p "Secret: " sec 
echo "Updating credentials...."
echo "export AWS_ACCESS_KEY_ID=`/home/pi/ukmon/.ukmondec $key k`" > $CREDFILE
echo "export AWS_SECRET_ACCESS_KEY=`/home/pi/ukmon/.ukmondec $sec s`" >> $CREDFILE
echo "export AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION" >> $CREDFILE
echo "export loc=$loc" >> $CREDFILE




