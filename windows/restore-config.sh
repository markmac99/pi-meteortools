#!/bin/bash
# Copyright (C) Mark McIntyre
echo $1
hn=$1

hn_u=${hn^^}

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
pushd $here
if [ ! -f $hn_u.ini ] ; then
    echo "ini file for $hn not found"
    exit 1
fi 
locf=$(grep LOCALFOLDER ../scripts/$hn_u.ini |sed 's/F:/\/mnt\/f/g'| awk -F= '{print $2}' | tr -d "\r")
pushd $locf/../config

if [ ! -d $hn ] ; then 
    echo backup of $hn not found
    exit 1
fi
cd $hn 

# RMS config and keys
scp platepar_cmn2010.cal ${hn}:source/RMS/
scp  mask.bmp ${hn}:source/RMS/
scp .config ${hn}:source/RMS/
scp .rmsautorunflag ${hn}:
scp .ssh/id_rsa* ${hn}:.ssh/
scp .ssh/id_ed* ${hn}:.ssh/
ssh ${hn} "chmod 0600 ~/.ssh/id_rsa"
ssh ${hn} "chmod 0644 ~/.ssh/id_rsa.pub"
ssh ${hn} "chmod 0600 ~/.ssh/id_ed25519"
ssh ${hn} "chmod 0644 ~/.ssh/id_ed25519.pub"

# ukmon config 
scp ukmon.ini ${hn}:source/ukmon-pitools/
scp .firstrun ${hn}:source/ukmon-pitools/ > /dev/null 2>&1
scp domp4s ${hn}:source/ukmon-pitools/ > /dev/null 2>&1
scp dotimelapse ${hn}:source/ukmon-pitools/ > /dev/null 2>&1
scp extrascript ${hn}:source/ukmon-pitools/ > /dev/null 2>&1
scp .ssh/ukmon* ${hn}:.ssh/
scp .ssh/authorized_keys ${hn}:.ssh/
scp .ssh/known_hosts ${hn}:.ssh/
ssh ${hn} "chmod 0600 ~/.ssh/ukmon"
ssh ${hn} "chmod 0644 ~/.ssh/ukmon.pub"
ssh ${hn} "chmod 0600 ~/.ssh/authorized_keys"
ssh ${hn} "chmod 0644 ~/.ssh/known_hosts"

# keys used by other processes
scp .ssh/config ${hn}:.ssh/
scp .ssh/gmail*.json ${hn}:.ssh/
scp .ssh/markskey.pem ${hn}:.ssh/
scp .ssh/mjmm-data.key ${hn}:.ssh/
ssh ${hn} "chmod 0644 ~/.ssh/config"
ssh ${hn} "chmod 0600 ~/.ssh/gmail*.json"
ssh ${hn} "chmod 0600 ~/.ssh/markskey.pem"
ssh ${hn} "chmod 0600 ~/.ssh/mjmm-data.key"

ansible-playbook /mnt/e/dev/meteorhunting/pi-meteortools/deploy-pi.yml --extra-vars "host=${hn}"
scp token.pickle $hn:mjmm
