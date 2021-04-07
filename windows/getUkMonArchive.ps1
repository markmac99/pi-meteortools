# script to get CSV files from UFO Archive

$curloc = get-location
set-location $PSScriptRoot

# load the helper functions
. .\helperfunctions.ps1

# read the inifile
$ini=get-inicontent 'archive.ini'
$keyfile=$ini['aws']['keyfile'] 
$consol=$ini['aws']['consolidatedfolder'] 
$archive=$ini['aws']['archivefolder'] 
$localconsol=$ini['local']['localconsol']
$localarch=$ini['local']['localarchive']
$fullday=[int]$ini['local']['fullday']

$oldkey = $Env:AWS_ACCESS_KEY_ID
$oldsec = $env:AWS_SECRET_ACCESS_KEY

$keys=((Get-Content $keyfile)[1]).split(',')
$Env:AWS_ACCESS_KEY_ID = $keys[2]
$env:AWS_SECRET_ACCESS_KEY = $keys[3]

Write-Output "syncing the consolidated data"
aws s3 sync $consol $localconsol --exclude "*" --include "*.csv" --exclude "*temp*"
if((get-date).day  -eq $fullday){
    Write-Output "syncing the raw data"
    aws s3 sync $archive $localarch --exclude "*" --include "*.csv" --include "*.txt" --include "*.xml" --exclude "*detlog.csv"
}else {
    Write-Output "not doing full dataset today"
}
$Env:AWS_ACCESS_KEY_ID = $oldkey
$env:AWS_SECRET_ACCESS_KEY = $oldsec
set-location $curloc