#
# powershell script to plot a map of RMS FTP files
#
$loc=get-location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
$thisdt=$args[0]

$inifname="analysis.ini"

if ((test-path $inifname) -eq $false) {
    write-output "ini file missing or invalid, can't continue"
    exit 1
}
$ini=get-inicontent $inifname
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']
$locfldr=$ini['fireballs']['localfolder']+'/..'

$fullpath=new-object string[] (4)

$pth= "${locfldr}/UK0006/ConfirmedFiles/UK0006_${thisdt}*/FTP*.txt"
$ftp=((get-item $pth).fullname | select-string -pattern "backup" -notmatch | select-string -pattern "pre-confirm" -notmatch)
$fullpath[0]=$ftp
$pth= "${locfldr}/UK000F/ConfirmedFiles/UK000F_${thisdt}*/FTP*.txt"
$ftp=((get-item $pth).fullname | select-string -pattern "backup" -notmatch | select-string -pattern "pre-confirm" -notmatch)
$fullpath[1]=$ftp
$pth= "${locfldr}/UK001L/ConfirmedFiles/UK001L_${thisdt}*/FTP*.txt"
$ftp=((get-item $pth).fullname | select-string -pattern "backup" -notmatch | select-string -pattern "pre-confirm" -notmatch)
$fullpath[2]=$ftp
$pth= "${locfldr}/UK002F/ConfirmedFiles/UK002F_${thisdt}*/FTP*.txt"
$ftp=((get-item $pth).fullname | select-string -pattern "backup" -notmatch | select-string -pattern "pre-confirm" -notmatch)
$fullpath[3]=$ftp

conda activate $rms_env
$env:pythonpath="$rms_loc"
set-location $rms_loc
python -m Utils.ShowerAssociation $fullpath[0] $fullpath[1] $fullpath[2] $fullpath[3] -c ${locfldr}/config/uk0006/.config
set-location $loc
