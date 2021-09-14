set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    $inifname='radio.ini'
}
else {
    $inifname = $args[0]
}
$ini=get-inicontent $inifname
$hostname=$ini['camera']['hostname']
$localfolder=$ini['camera']['localfolder']
$remfldr=$ini['camera']['remotefolder']
$remuser=$ini['camera']['remoteuser']
$rempass=(get-content $ini['camera']['remotepass'])

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

$srcfldr = $rempath + '\screenshots'
$locfolder = $localfolder + '\screenshots'
robocopy $srcfldr $locfolder *latest*.*    /dcopy:DAT /tee /m /v /s /r:3

# create next month's empty RMOB file, if it doesn't already exist
#$nexmth=(get-date).adddays(8).tostring("yyyyMM")
#$fname = -join($rempath,"\RMOB-", $nexmth, ".DAT")
#if((test-path $fname) -eq $false) 
#{ 
#    write-output "creating empty file...." 
#    new-item -path $fname 
#}
net use $rempath  /d

#write-output "archiving old data" 

# delete older files to save space
#$prvmth = (get-date).addmonths(-2) 
#$ccyymm=get-date($prvmth) -uformat('%Y%m')
#$yymm=get-date($prvmth) -uformat('%y%m')
#$srcs = 'event_log'+$ccyymm+'*.txt'
#$archfile = 'event_log'+$ccyymm+'.zip'
#get-childitem -path $srcs | compress-archive -destinationpath $archfile -Update
#remove-item $srcs
#Set-Location screenshots
#$srcs = 'event'+$yymm+'*.jpg'
#$archfile = 'event'+$yymm+'.zip'
#get-childitem -path $srcs | compress-archive -destinationpath $archfile -Update
#Remove-Item $srcs
#Set-Location ..

set-location $PSScriptRoot
.\PushRadioData.ps1 
write-output "done" 
