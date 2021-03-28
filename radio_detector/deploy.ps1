# powershell script to deploy to my radio detector
#
# read the ini file and get the target location
. .\helperfunctions.ps1
$inifname = './station.ini'
if ((test-path $inifname) -eq $false) {
    write-output "station.ini file missing or invalid, can't continue"
    exit 1
}
$ini=get-inicontent $inifname
$hostname=($ini['host']['hostname']).replace('/','\')
$datadir=($ini['host']['datadir']).replace('/','\')
$targ='\\'+$hostname+'\'+$datadir+'\scripts'

# do the actual deployment

xcopy /dy /exclude:exclude.rsp *.* $targ
xcopy /dy e:\dev\aws\ukmon-shared.csv $targ
