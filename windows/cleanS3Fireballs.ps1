# powershell script to clean the non-fireballs out of S3
#
$curloc = get-location
set-location $PSScriptRoot

# load the helper functions
. .\helperfunctions.ps1

# read the inifile
$ini=get-inicontent 'live.ini'
$remotefolder=$ini['live']['remotefolder'] 
$fbfolder=$ini['live']['fbfolder'] 
$awsprofile = $ini['aws']['awsprofile']

set-location $fbfolder
set-location .\mp4s

$mthtoget=read-host -prompt 'Enter month to purge eg 202007'
$incl='M' + $mthtoget + '*.mp4'

Write-Output "purging MP4s"
aws s3 sync . $remotefolder --exclude "*" --include $incl --delete --profile $awsprofile

Write-Output "purging AVIs, if any"
$flist=(Get-ChildItem ..\*.avi)
for($i=0;$i -lt $flist.count ; $i++ ){
	$fn=$flist[$i].basename
	$mp4=$fn+'.mp4'
	$avi=$fn+'.avi'
	if((test-path $mp4) -eq $false){
		write-output 'removing $avi'
		Write-Output "Remove-Item ..\$avi"
	}
}
Write-Output "Done"
set-location $curloc
pause
