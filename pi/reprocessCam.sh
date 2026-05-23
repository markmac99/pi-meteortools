#!/bin/bash
source ~/vRMS/bin/activate

cd ~/source/RMS

camid=$1
dtval=$2
if [[ "$camid" == "" || "$dtval" == "" ]] ; then 
	echo usage: reprocessCam.sh camid dtstr
	exit
fi
capdircnt=$(ls -1d ~/RMS_data/${camid}/CapturedFiles/${camid}_${dtval}* | wc -l)
if [ $capdircnt -gt 1 ]; then
	echo "more than one matching folder found, please refine the date"
	echo $capdir
	exit
fi 
capdir=$(ls -1d ~/RMS_data/${camid}/CapturedFiles/${camid}_${dtval}*)
arcdir=${capdir/Capture/Archive}
echo ""
if [[ "$capdir" == "" || "$arcdir" == "" ]] ; then 
	echo data not found for $camid and $dtval
	exit
fi 
grep extl_script ~/source/RMS/RMS/Reprocess.py > /dev/null 2>&1
if [ $? -eq 0 ] ; then
	python -m RMS.Reprocess -e -c ~/source/Stations/${camid}/.config   ${capdir}
else
	python -m RMS.Reprocess -c ~/source/Stations/${camid}/.config   ${capdir}
	python -m RMS.RunExternalScript -c ~/source/Stations/${camid}/.config  ${capdir} ${arcdir}
fi