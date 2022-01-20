set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    $inifname='radiostation.ini'
}
else {
    $inifname = $args[0]
}
$ini=get-inicontent $inifname
$hostname=$ini['detectionpc']['hostname']
$localfolder=$ini['detectionpc']['localfolder']
$remfldr=$ini['detectionpc']['remotefolder']
$remuser=$ini['detectionpc']['remoteuser']
$rempass=(get-content $ini['detectionpc']['remotepass'])

$yy = (get-date -uformat '%Y')
$ym = (get-date -uformat '%Y%m')
$yd = (get-date -uformat '%Y%m%d')

set-location $localfolder

# now grab the latest radio data and process it
write-output "copying files" 
$remfldr = $remfldr.replace("/","\")
$rempath='\\'+$hostname+$remfldr

net use $rempath /user:$remuser $rempass
if ($? -ne "True")  {
    Send-MailMessage -from radio@observatory -to mark@localhost -subject "Radio: Unable co connect" -body "unable to connect to radio detector" -smtpserver 192.168.1.151    
    set-location $PSScriptRoot
    exit 2
} 
$srcfldr = $rempath + '\screenshots'
$locfolder = $localfolder + '\screenshots\' + $yy + '\' + $ym + '\' + $yd
$fils = 'event' + $yd + '*.jpg'
robocopy $srcfldr $locfolder $fils /dcopy:DAT /tee /mov /v /s /r:3

$srcfldr = $rempath + '\sounds'
$locfolder = $localfolder + '\sounds\' + $yy + '\' + $ym + '\' + $yd
$fils = 'event' + $yd + '*.wav'
robocopy $srcfldr $locfolder $fils /dcopy:DAT /tee /mov /v /s /r:3

$srcfldr = $rempath + '\logs'
$locfolder = $localfolder + '\logs'
robocopy $srcfldr $locfolder *.*    /dcopy:DAT /tee /m /v /s /r:3

$srcfldr = $rempath + '\RMOB'
$locfolder = $localfolder + '\RMOB'
robocopy $srcfldr $locfolder *.*    /dcopy:DAT /tee /m /v /s /r:3

net use $rempath  /d

set-location $PSScriptRoot
.\PushRadioData.ps1 
write-output "done" 
