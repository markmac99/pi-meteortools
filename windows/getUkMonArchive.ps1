# script to get CSV files from UFO Archive

$curloc = get-location
set-location $PSScriptRoot

# load the helper functions
. .\helperfunctions.ps1

# read the inifile
$ini=get-inicontent 'archive.ini'
$awsprofile = $ini['aws']['awsprofile']
$consol=$ini['aws']['consolidatedfolder'] 
$archive=$ini['aws']['archivefolder'] 
$localconsol=$ini['local']['localconsol']
$localarch=$ini['local']['localarchive']
$fullday=[int]$ini['local']['fullday']

Write-Output "syncing the consolidated data"
aws s3 sync $consol $localconsol --exclude "*" --include "*.csv" --exclude "*temp*" --profile $awsprofile
if((get-date).day  -eq $fullday){
    Write-Output "syncing the raw data"
    aws s3 sync $archive $localarch --exclude "*" --include "*.csv" --include "*.txt" --include "*.xml" --exclude "*detlog.csv" --profile $awsprofile
}else {
    Write-Output "not doing full dataset today"
}
set-location $curloc