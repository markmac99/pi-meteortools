# Copyright (C) Mark McIntyre
set-location $PSScriptRoot
$now=(get-date -uformat '%Y%m%d')
$logf="..\logs\"+$now+".log"

Write-Output "starting to get all data" | tee-object $logf
.\getDataFromCamera.ps1 .\UK0006.ini | tee-object $logf -append
.\getDataFromCamera.ps1 .\UK000F.ini | tee-object $logf -append
.\getDataFromCamera.ps1 .\UK001L.ini | tee-object $logf -append
.\getDataFromCamera.ps1 .\UK002F.ini | tee-object $logf -append
.\getDataFromRadio.ps1 | tee-object $logf -append
Write-Output "got all data" | tee-object $logf -append

set-location $PSScriptRoot

$dt= (get-date -uformat '%Y-%m-%d %H:%M:%S')
write-output "getall finished at $dt"| tee-object $logf -append
