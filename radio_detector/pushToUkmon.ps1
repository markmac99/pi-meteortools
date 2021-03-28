# 
# powershell script to push the radio CSV files to ukmon
#
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
$logf=$datadir+'/logs/ukmon-'+(get-date -uformat '%Y%m%d')+'.log'
$ukmonkey=$ini['ukmon']['ukmon_keyfile']
$keys=((Get-Content $ukmonkey)[1]).split(',')
$Env:AWS_ACCESS_KEY_ID = $keys[0]
$env:AWS_SECRET_ACCESS_KEY = $keys[1]

$station=$ini['ukmon']['ukmon_station']
$srcloc=$datadir+'\csv\'
write-output 'updating ukmon' | tee-object $logf 
$s3targ='s3://ukmon-shared/archive/' + $station + '/Radio/'
aws s3 sync $srcloc $s3targ | tee-object $logf -append
set-location $PSScriptRoot