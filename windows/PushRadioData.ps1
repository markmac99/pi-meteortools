#
# powershell script to generate heatmaps and push them to a website
#
set-location $PSScriptRoot
. .\helperfunctions.ps1
$inifname = './radiostation.ini'
if ((test-path $inifname) -eq $false) {
    write-output "radiostation.ini file missing or invalid, can't continue"
    exit 1
}

$ini=get-inicontent $inifname
$datadir=($ini['detector']['datadir']).replace('/','\')

if((test-path $inifname) -eq $false){
    write-output "datadir missing or invalid, can't continue"
    exit 2
}
$RMS_ENV = $ini['RMS']['RMS_ENV']
conda activate $RMS_ENV

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

$ssloc=$datadir+'\screenshots'
set-location $ssloc

write-output "copying latest 2d image" | tee-object $logf -append
scp -o StrictHostKeyChecking=no -i $key latest2d.jpg $targ

$curdt=(get-date -uformat '%Y%m%d')
$yy=$curdt.substring(0,4)
$ym=$curdt.substring(0,6)
$curpth="$yy\$ym\$curdt\event$curdt*.jpg"
$fnam=(get-childitem  $curpth | sort-object lastwritetime).fullname | select-object -last 1
if((test-path $fnam) -eq 1 ){
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

# push to UKMON
$logf=$datadir+'/logs/ukmon-'+(get-date -uformat '%Y%m%d')+'.log'
$ukmonkey=$ini['ukmon']['ukmon_keyfile']
$station=$ini['ukmon']['ukmon_station']
. $ukmonkey

$srcloc=$datadir+'\csv\'
write-output 'updating ukmon' | tee-object $logf 
$s3targ='s3://ukmon-shared/archive/' + $station + '/'
aws s3 sync $srcloc $s3targ | tee-object $logf -append

# now push to my own archive
scp $datadir\rmob\$yy\$ym\$ym.jpg ukmonhelper:data/Radio/$yy/ 

# create index for the rmob history
set-location $PSScriptRoot
