#!/bin/bash
# Copyright (C) Mark McIntyre

function backuphost() {
    echo $1
    hn=$1
    hn_u=${hn^^}

    if [ ! -f $hn_u.ini ] ; then
        echo "ini file for $hn not found"
        exit 1
    fi 
    locf=$(grep LOCALFOLDER ../scripts/$hn_u.ini |sed 's/F:/\/mnt\/f/g'| awk -F= '{print $2}' | tr -d "\r")
    pushd $locf/../config

    mkdir $hn > /dev/null 2>&1

    rsync ${hn}:source/RMS/platepar* $hn/
    rsync ${hn}:source/RMS/mask* $hn/
    rsync ${hn}:source/RMS/.config $hn/
    rsync ${hn}:.rmsautorunflag $hn/ > /dev/null 2>&1

    #ssh keys and config
    rsync -avz ${hn}:.ssh/* $hn/.ssh/

    # ukmon settings
    rsync ${hn}:source/ukmon-pitools/ukmon.ini $hn
    rsync ${hn}:source/ukmon-pitools/.firstrun $hn > /dev/null 2>&1
    rsync ${hn}:source/ukmon-pitools/domp4s $hn > /dev/null 2>&1
    rsync ${hn}:source/ukmon-pitools/dotimelapse $hn > /dev/null 2>&1
    rsync ${hn}:source/ukmon-pitools/extrascript $hn > /dev/null 2>&1

    # mjmm settings
    scp $hn:mjmm/*.pickle $hn/ > /dev/null 2>&1
    scp $hn:mjmm/config.ini $hn/ > /dev/null 2>&1

    popd
}

# backup everything
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
pushd $here

if [ $# -lt 1 ] ; then 
    backuphost uk0006
    backuphost uk000f
    backuphost uk002f
    backuphost uk001l
else
    backuphost $1
fi
popd 
