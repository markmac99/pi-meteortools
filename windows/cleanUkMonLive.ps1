#
# script to remove bad data from livestream including bad fireballs
# Copyright (C) Mark McIntyre
#

$curloc = get-location
set-location $PSScriptRoot

# load the helper functions
. .\helperfunctions.ps1

# read the inifile
$ini=get-inicontent 'archive.ini'
$awsprofile = $ini['live']['awsprofile']
$remotefolder=$ini['live']['remotefolder'] 
$fbfolder=$ini['live']['fbfolder'] 
$remotebad=$ini['live']['remotebad'] 

if($args.count -eq 0){$dr='--dryrun'} else {$dr=''}

$msg='will delete the following:'
Write-Output $msg
#aws s3 sync $localfolder  $remotefolder --exclude "*" --include "*.jpg" --include "*.xml" --exclude "*temp*" --delete $dr
aws s3 sync $fbfolder $remotefolder --exclude "*" --include "*.mp4" --exclude "*temp*" $dr --delete --profile $awsprofile
aws s3 rm $remotebad --include "*" --recursive

set-location $curloc