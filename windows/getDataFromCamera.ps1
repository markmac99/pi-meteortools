# script to copy/move data from a remote Pc or Pi running a camer to
# a central location for analysis purposes
#
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
$hostname=$ini['camera']['hostname']
$camname=$ini['camera']['camera_name']
$locfldr=$ini['camera']['localfolder']
$isufo=$ini['camera']['UFO']
$remuser=$ini['camera']['remoteuser']
$rempass=(get-content $ini['camera']['remotepass'])

Write-Output "Getting data from $camname" (get-date) 

$loopctr=0
ping -n 1 $hostname
while (($? -ne "True") -and ($loopctr -lt 10))  {
    Start-Sleep 30
    ping -n 1 -4 $hostname
    $loopctr++
}
if ($loopctr -eq 10)  {
    Send-MailMessage -from $hostname@oservatory -to mark@localhost -subject "astromini down" -body "$hostname seems to be down, check power and network" -smtpserver 192.168.1.151    
    exit 1
}
set-location $locfldr

if ($isufo -eq 1){
    write-output "processing UFO camera "
    $remfldr=$ini['camera']['remotefolder']
    $tod=((get-date).tostring("yyyy\\yyyyMM"))
    $ytd=((get-date).adddays(-1).tostring("yyyy\\yyyyMM"))
    if ((test-path $tod) -eq $false) {
        mkdir $tod
    }
    if ((test-path $ytd) -eq $false) {
        mkdir $ytd
    }
    $remfldr = $remfldr.replace("/","\")
    $rempth='\\'+$hostname+$remfldr
    net use $rempth /user:$remuser $rempass
    $src=$rempth+'\'+$tod

    Write-Output "copying data for $src to $tod" 

    robocopy $src $tod *.jpg *.bmp *.txt *.xml M*.avi M*.mp4 /dcopy:DAT /tee /v /s /r:3 /mov /z /np
    if ($tod -ne $ytd) {
        Write-Output "copying data for $ytd"
        robocopy $rempth\$ytd $ytd *.jpg *.bmp *.txt *.xml M*.avi M*.mp4 /dcopy:DAT /tee /v /s /r:3 /mov /z  /np
    }
    net use $rempth /d >> c:\temp\log.log
}
else {
    Write-Output "processing RMS camera"
    $remfldr= '\\'+$hostname+'\rms_share\ArchivedFiles'
    $dirlist=(get-childitem $remfldr -directory)
    for ($i=0;$i -lt $dirlist.length; $i++) { 
        $dn=$dirlist[$i].name 
        $locpth='ArchivedFiles\'+$dn
        $tp=(test-path $locpth)
        if ($tp -eq $true){
            $lrt=$dirlist[$i].lastwritetime
            $lp=$locpth+'*'
            $llt=(get-childitem $lp -directory).lastwritetime   
            if ($llt -lt $lrt){
                $rmpth=$remfldr+'\'+$dn
                robocopy $rmpth  $locpth /dcopy:DAT /tee /v /s /r:3 /np /z /xf *.bz2
                (get-item $locpth).lastwritetime=(get-date)
            }
        }
        else{
            $rmpth=$remfldr+'\'+$dn
            robocopy $rmpth $locpth /dcopy:DAT /tee /v /s /r:3 /np /z /xf *.bz2
        }
    }
    $remfldr= '\\'+$hostname+'\rms_share\logs'
    robocopy $remfldr logs /dcopy:DAT /tee /v /s /r:3 

    Set-Location $psscriptroot
    .\reorgByYMD.ps1 $inifname
}
Set-Location $psscriptroot
Write-Output "finished" (get-date) 
exit 0
