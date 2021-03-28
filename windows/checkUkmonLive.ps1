# check the files against latest algo

$loc=get-location
Set-Location $psscriptroot

# load the helper functions
. .\helperfunctions.ps1

# read the inifile
$ini=get-inicontent 'live.ini'

#$keyfile=$ini['live']['keyfile'] 
#$remotefolder=$ini['live']['remotefolder'] 
#$localfolder=$ini['camera']['localfolder'] 
$confbad=$ini['cleaning']['badfolder'] 
$rmsenv=$ini['rms']['rms_env'] 

#move bad\*.xml .
#move bad\*.jpg .

Remove-Item $confbad/results.txt
conda activate $rmsenv
python curateFolder.py live.ini
set-location $loc
