#!/bin/bash

cd /mnt/f/videos/meteorcam/support
ssh ukmonhelper2 "ls -1 /var/sftp/logupload/logs/*.tgz" > /tmp/list.txt
echo Quit >> /tmp/list.txt
readarray -t list < /tmp/list.txt

PS3='Please enter your choice or 0 to exit: '
select selection in "${list[@]}"; do
    if [[ $REPLY == "0" ]]; then
        echo 'Goodbye' >&2
        exit
    else
        # echo $REPLY $selection
        break
    fi
done
echo "processing $selection"
bn=$(basename $selection .tgz)
mkdir $bn
scp ukmonhelper2:$selection .
cd $bn
tar xvf ../$bn.tgz
ssh ukmonhelper2 "rm -f $selection"
