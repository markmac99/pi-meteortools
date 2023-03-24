# simple script to copy then display the most recent UFO meteor captures
# and allow analysis / sanity checking before optionally uploading to UKMON
# Copyright (C) Mark McIntyre

set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    write-output "ini file missing, can't continue"
    exit 1
}
$inifname = $args[0]

$ini=get-inicontent $inifname
$hostname=$ini['camera']['hostname']
$remotefolder=$ini['camera']['remotefolder']
$localfolder=$ini['camera']['localfolder']
$UFOPATH=$ini['ufo']['UFOPATH']
$UFOBINARY=$ini['ufo']['UFOBINARY']
$UKMON_ENV=$ini['ukmon']['UKMON_Env']
$DOCLEANING=$ini['cleaning']['DOCLEANING']

# copy the latest data from the source
$yy=(get-date -uformat '%Y')
$yymm=(get-date -uformat '%Y%m')
$srcpath='\\'+$hostname+$remotefolder+'/'+$yy+'/'+$yymm
$destpath=$localfolder+'/'+$yy+'/'+$yymm
robocopy $srcpath $destpath /dcopy:DAT /tee /m /v /s /r:3 /mov

if ($DOCLEANING -eq 1){
    conda activate $UKMON_ENV
    $dt=(get-date).adddays(-1).tostring('yyyyMMdd')
    python CurateUFO.py $inifname $dt
    $dt=(get-date).tostring('yyyyMMdd')
    python CurateUFO.py $inifname $dt
}
Set-location $UFOPATH
$ufo=$UFOPATH+'/'+$UFOBINARY
& $ufo | out-null
set-location $PSScriptRoot

.\UploadToUkMon.ps1 $inifname
#pause
