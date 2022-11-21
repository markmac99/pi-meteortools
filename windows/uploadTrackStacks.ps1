#
# upload trackstacks to website
#

$loc = get-location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1

if ($args.count -eq 0) {
    write-output "ini file missing, can't continue"
    exit 1
}
$inifname = $args[0]
$ini=get-inicontent $inifname
$hostname=$ini['camera']['hostname']
$localfolder=$ini['camera']['localfolder']

$awsprofile=$ini['mjmm']['awsprofile']

$srcpath=$localfolder + '\..\trackstacks\'
$hnu = $hostname.toupper()
$dirname = "s3://mjmm-data/" + $hnu + "/trackstacks/"
aws s3 sync $srcpath $dirname --exclude "*" --include "$hnu*" --profile $awsprofile

set-location $loc


