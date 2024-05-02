#!/bin/bash
#
# script to check and restart allsky if frozen
# Copyright (C) Mark McIntyre
#

srcdir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $srcdir
source ~/vAllsky/bin/activate

isrunning=$(systemctl show -p SubState --value allsky)

if [ "$isrunning" == "running" ] ; then
    working=$(find /var/log -maxdepth 1 -name "allsky.log" -type f -mmin -5)

    if [ "$working" == "" ] ; then
        echo allsky not logging, probably dead
        echo sudo systemctl restart allsky
    else
        echo all fine
    fi
fi