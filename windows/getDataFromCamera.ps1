# Copyright (C) Mark McIntyre
# script to copy/move data from a remote Pc or Pi running a camer to
# a central location for analysis purposes
# Copyright (C) 2018-2023 Mark McIntyre
#
#
$loc = get-location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    write-output "ini file missing, can't continue"
    exit 1
}

$inifname = $args[0]
if ((test-path $inifname) -eq $false) {
    write-output "ini file missing or invalid, can't continue"
    exit 1
}

$ini=get-inicontent $inifname
$remotepth=$ini['camera']['hostname']
$localfolder=$ini['camera']['localfolder']
$hostname=(split-path $remotepth -leaf)

Write-Output "Getting data from $hostname" (get-date) 

$loopctr=0
ping -n 1 $hostname
while (($? -ne "True") -and ($loopctr -lt 10))  {
    Start-Sleep 30
    ping -n 1 -4 $hostname
    $loopctr++
}
if ($loopctr -eq 10)  {
    Send-MailMessage -from $hostname@oservatory -to mark@localhost -subject "$hostname down" -body "$hostname seems to be down, check power and network" -smtpserver 192.168.1.151    
    exit 1
}
set-location $localfolder

$destpath=$localfolder+'\ArchivedFiles'
$destpath_l ="/mnt/" +$destpath.replace(':','').tolower().replace('\','/')

write-output "checking bash"
& C:\Windows\System32\bash.exe --version
write-output "running rsync"
& C:\Windows\System32\bash.exe -c "rsync -avz --exclude=UK*.bz2 ${hostname}:RMS_data/ArchivedFiles/ ${destpath_l}"
& C:\Windows\System32\bash.exe -c "rsync -avz --exclude=UK*.bz2 ${hostname}:RMS_data/logs/ ./logs"

Set-Location $loc
Write-Output "finished" (get-date) 
exit 0
