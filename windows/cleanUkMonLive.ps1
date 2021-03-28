#
# script to remove bad data from livestream including bad fireballs
#

$curloc = get-location
set-location $PSScriptRoot

# load the helper functions
. .\helperfunctions.ps1

# read the inifile
$ini=get-inicontent 'archive.ini'
$keyfile=$ini['live']['keyfile'] 
$remotefolder=$ini['live']['remotefolder'] 
#$localfolder=$ini['live']['localfolder'] 
$fbfolder=$ini['live']['fbfolder'] 
$remotebad=$ini['live']['remotebad'] 

if($args.count -eq 0){$dr='--dryrun'} else {$dr=''}

$oldkey = $Env:AWS_ACCESS_KEY_ID
$oldsec = $env:AWS_SECRET_ACCESS_KEY

$keys=((Get-Content $keyfile)[1]).split(',')
$Env:AWS_ACCESS_KEY_ID = $keys[0]
$env:AWS_SECRET_ACCESS_KEY = $keys[1]

$msg='will delete the following:'
Write-Output $msg
#aws s3 sync $localfolder  $remotefolder --exclude "*" --include "*.jpg" --include "*.xml" --exclude "*temp*" --delete $dr
aws s3 sync $fbfolder $remotefolder --exclude "*" --include "*.mp4" --exclude "*temp*" $dr --delete 
aws s3 rm $remotebad --include "*" --recursive

$Env:AWS_ACCESS_KEY_ID = $oldkey
$env:AWS_SECRET_ACCESS_KEY = $oldsec
set-location $curloc