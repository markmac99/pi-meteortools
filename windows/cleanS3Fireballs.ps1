# powershell script to clean the non-fireballs out of S3
#
$curloc = get-location
set-location $PSScriptRoot

# load the helper functions
. .\helperfunctions.ps1

# read the inifile
$ini=get-inicontent 'live.ini'
$keyfile=$ini['live']['keyfile'] 
$remotefolder=$ini['live']['remotefolder'] 
$fbfolder=$ini['live']['fbfolder'] 

$oldkey = $Env:AWS_ACCESS_KEY_ID
$oldsec = $env:AWS_SECRET_ACCESS_KEY

$keys=((Get-Content $keyfile)[1]).split(',')
$Env:AWS_ACCESS_KEY_ID = $keys[0]
$env:AWS_SECRET_ACCESS_KEY = $keys[1]

set-location $fbfolder
set-location .\mp4s

$mthtoget=read-host -prompt 'Enter month to purge eg 202007'
$incl='M' + $mthtoget + '*.mp4'

Write-Output "purging MP4s"
aws s3 sync . $remotefolder --exclude "*" --include $incl --delete

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
$Env:AWS_ACCESS_KEY_ID = $oldkey
$env:AWS_SECRET_ACCESS_KEY = $oldsec
pause
