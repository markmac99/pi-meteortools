#!/bin/bash
#
# Simple script to create a stack of the last ten FF files and push it to 
# a website of your choice using SCP
# Requires: you must supply values for USER, SERVER, TARGET folder and SSHKEY
# the SSHKEY must be USER@SERVER's standard SSH private key. 
#
USER=targetuser
SERVER=targetserver
TARGET=targetfolder
SSHKEY=usersshkey

cd /home/pi/source/RMS
DISPLAY=:0.0
TOD=`ls -1 /home/pi/RMS_data/CapturedFiles/ | tail -1`
CAPDIR=/home/pi/RMS_data/CapturedFiles/${TOD}

FTC=`ls -1 $CAPDIR/FF* | tail -10`
mkdir /tmp/towebsite> /dev/null 2>&1
rm -f /tmp/towebsite/*
cp ${FTC} /tmp/towebsite
python -m Utils.StackFFs -x /tmp/towebsite jpg
JPG=`ls -1 /tmp/towebsite/*.jpg | tail -1`
mv ${JPG} /tmp/towebsite/latest-stack.jpg
JPG=/tmp/towebsite/latest-stack.jpg
echo ${JPG}

scp -i ${SSHKEY} ${JPG} ${USER}@${SERVER}:${TARGET}

rm -f /tmp/towebsite/*

