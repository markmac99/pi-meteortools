# powershell script to backup the meteorcam data
# Copyright (C) Mark McIntyre
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
$ini = get-inicontent "archive.ini"
$localfolder = $ini['backup']['localfolder']
$target = $ini['backup']['target']
$cams = $ini['backup']['cameras']
$extras = $ini['backup']['extras']
$camfldrs = $ini['backup']['camfldrs']

$src = $localfolder
$dest = $target
$cl = $cams.split(',')
$xl = $extras.split(',')
$cf = $camfldrs.split(',')

$CurrentDate = Get-Date
$daysback=190
$DatetoDelete = $CurrentDate.AddDays(-$Daysback)

$yr = [int](get-date -uformat '%Y')
$syr=$yr-3

write-output "archiving derived data"
foreach ($x in $xl)
{
    write-output "$x"
    $ssrc=$src + $x
    $sdest=$dest + $x
    if ($x -eq "mthlystacks") {
        robocopy $ssrc $sdest /dcopy:DAT /m /z /r:3
    }else {
        robocopy $ssrc $sdest /dcopy:DAT /m /s /z /r:3
    }
    
}

write-output "archiving camera data"
foreach ($cam in $cl)
{    
    foreach ($c in $cf)
    {
        write-output "Processing $c for $cam"
        $ssrc=$src+$cam+'\'+$c
        $sdest=$dest+$cam+'\'+$c
        Write-Output $ssrc $sdest
        if (test-path $ssrc)
        {
            robocopy $ssrc $sdest /dcopy:DAT /move /s /z /r:3 /minage:$daysback
            $fldrs = (get-item $ssrc\*)
            foreach ($fldr in $fldrs) {
                if (get-item $fldr | where-object { $_.creationtime -lt $DatetoDelete }) { 
                    write-output "removing $fldr" 
                    Remove-Item $fldr -recurse -force
                }
            }
        }
    }
    for ($i=$syr; $i -le $yr; $i++ )
    {
        write-output "Processing $i for $cam"
        $ssrc=$src+$cam+'\'+$i
        $sdest=$dest+$cam+'\'+$i 
        Write-Output $ssrc $sdest
        if (test-path $ssrc)
        {
            robocopy $ssrc $sdest /dcopy:DAT /move /s /z /r:3 /minage:$daysback
            write-output "now removing old folders"
            $fldrs = (get-item $ssrc\*)
            foreach ($fldr in $fldrs) {
                if (get-item $fldr | where-object { $_.creationtime -lt $datetodelete }) {
                    write-output "removing $fldr" 
                    Remove-Item $fldr -recurse -force
                }
            }
        }
    }
}
pause
