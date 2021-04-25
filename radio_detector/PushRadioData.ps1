#
# powershell script to generate heatmaps and push them to a website
#
set-location $PSScriptRoot
. .\helperfunctions.ps1
$inifname = './station.ini'
if ((test-path $inifname) -eq $false) {
    write-output "station.ini file missing or invalid, can't continue"
    exit 1
}

$ini=get-inicontent $inifname
$datadir=($ini['detector']['datadir']).replace('/','\')
if((test-path $inifname) -eq $false){
    write-output "datadir missing or invalid, can't continue"
    exit 2
}
$logf=$datadir+'/logs/process-'+(get-date -uformat '%Y%m%d')+'.log'
write-output 'updating colorgrammes' | tee-object $logf
Set-Location $PSScriptRoot
$srcdir=$datadir+'/logs'
$targdir=$datadir+'/rmob'
python .\colorgram.py $srcdir $targdir | tee-object $logf -append

write-output "Copying to website..." | tee-object $logf -append

# collect details about your website. 
$sitename=$ini['website']['sitename']
$targetdir=$ini['website']['targetdir']
$userid=$ini['website']['userid']
$key=$ini['website']['key']
$targ= $userid+'@'+$sitename+':'+$targetdir

#write-output "copying latest 2d image" | tee-object $logf -append
#set-location $datadir
#scp -o StrictHostKeyChecking=no -i $key latest2d.jpg $targ

$ssloc=$datadir+'\screenshots'
set-location $ssloc

$curdt=(get-date -uformat '%Y%m%d')
$fnam=(get-childitem  event$curdt*.jpg | sort-object lastwritetime).name | select-object -last 1
if($fnam){
    Write-Output 'copying last capture' | tee-object $logf -append
    copy-item $fnam  -destination latestcapture.jpg
    scp -o StrictHostKeyChecking=no -i $key latestcapture.jpg $targ
}else{
    write-output 'no capture yet today' | tee-object $logf -append
}

Write-Output 'copying colorgramme file' | tee-object $logf -append
#$mmyyyy=((get-date).tostring("MMyyyy"))
$srcfile=$datadir+'\RMOB\RMOB_latest.jpg'
copy-item $srcfile -destination .
$fnam='RMOB_latest.jpg'
scp -o StrictHostKeyChecking=no -i $key $fnam $targ

$srcfile=$datadir+'\RMOB\3months_latest.jpg'
copy-item $srcfile -destination .
$fnam='3months_latest.jpg'
scp -o StrictHostKeyChecking=no -i $key $fnam $targ

$msg=(get-date -uformat '%Y%m%d-%H%M%S')+' done'
write-output $msg | tee-object $logf -append
set-location $PSScriptRoot
.\pushToUkmon.ps1 