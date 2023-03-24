# check the files against latest algo
# Copyright (C) Mark McIntyre

$loc=get-location
Set-Location $psscriptroot

# load the helper functions
. .\helperfunctions.ps1

# read the inifile
$ini=get-inicontent 'live.ini'

$pylib=$ini['cleaning']['pylib']
$confbad=$ini['cleaning']['badfolder'] 
$rmsenv=$ini['rms']['rms_env'] 

if ((test-path $confbad/results.txt) -eq 1){
    Remove-Item $confbad/results.txt
}
conda activate $rmsenv
$oldpypath=$env:pythonpath
$env:pythonpath=$pylib
python -m ufoutils.curateFolder live.ini
$env:pythonpath=$oldpypath
set-location $loc
