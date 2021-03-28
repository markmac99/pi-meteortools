set-location $PSScriptRoot
$now=(get-date -uformat '%Y%m%d')
$logf="..\logs\"+$now+".log"

Write-Output "starting to get all data" | tee-object $logf -append
.\getDataFromCamera.ps1 .\tackley_ne.ini | tee-object $logf -append
.\getDataFromCamera.ps1 .\UK0006.ini | tee-object $logf -append
.\getDataFromCamera.ps1 .\UK000F.ini | tee-object $logf -append
.\getDataFromCamera.ps1 .\UK001L.ini | tee-object $logf -append
.\getDataFromRadio.ps1 | tee-object $logf -append
Write-Output "got all data" | tee-object $logf -append

set-location $PSScriptRoot

write-output "curating UFO cameras" | tee-object $logf -append
conda activate RMS

$dt=get-date -uformat '%Y%m%d'
write-output "processing $dt NE" | tee-object $logf -append
$res = python .\curateUFO.py .\tackley_ne.ini $dt
write-output $res | tee-object $logf -append

$dt=(get-date).adddays(-1).tostring('yyyyMMdd')
write-output "processing $dt" | tee-object $logf -append

write-output "processing $dt NE" | tee-object $logf -append
$res = python .\curateUFO.py .\tackley_ne.ini $dt
write-output $res | tee-object $logf -append

write-output "done" | tee-object $logf -append

set-location $PSScriptRoot
if ((get-date).hour -eq 20 ) {
    write-output "refreshing website" | tee-object $logf -append
    .\pushtowebsite.ps1 | tee-object $logf -append
}
if ((get-date).hour -eq 10)
{
    write-output "getting possible interesting events" | tee-object $logf -append
    $dtstr=((get-date).adddays(-1)).tostring('yyyyMMdd')
    .\getPossibles .\UK0006.ini $dtstr
    .\getPossibles .\UK000F.ini $dtstr
    .\getPossibles .\UK001L.ini $dtstr
}
.\loadMySQL.ps1 .\tackley_ne.ini

$dt= (get-date -uformat '%Y-%m-%d %H:%M:%S')
write-output "getall finished at $dt"| tee-object $logf -append
