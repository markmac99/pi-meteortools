# Copyright (C) Mark McIntyre
#
# powershell script to plot a map of RMS FTP files
#
$loc=get-location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1

$fromdt=[string]$args[0]
$sdt=[datetime]($fromdt.substring(0,4)+'-'+$fromdt.substring(4,2)+'-'+$fromdt.substring(6,2))

if($args.count -gt 1) {
    $todt=[string]$args[1]
    $edt=[datetime]($todt.substring(0,4)+'-'+$todt.substring(4,2)+'-'+$todt.substring(6,2))
}
else {
    $edt = $sdt
}

# read the inifile
$inifname="analysis.ini"

if ((test-path $inifname) -eq $false) {
    write-output "ini file missing or invalid, can't continue"
    exit 1
}
$ini=get-inicontent $inifname
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']
$locfldr=$ini['fireballs']['localfolder']+'/..'

while ($sdt -le $edt)
{
    $thisdt = $sdt.tostring('yyyyMMdd')
    foreach ($cam in "UK0006","UK000F","UK001L","UK002F")
    {
        $pth= "${locfldr}/${cam}/ConfirmedFiles/${cam}_${thisdt}*/FTP*.txt"
        $ftp=((get-item $pth).fullname | select-string -pattern "backup" -notmatch | select-string -pattern "pre-confirm" -notmatch)
        if (("x"+$ftp) -ne "x") {
            copy-item $ftp $locfldr/radiants/temp
        }
    }
    $sdt = $sdt.adddays(1)
}
conda activate $rms_env
$env:pythonpath="$rms_loc"
set-location $rms_loc
python -m Utils.ShowerAssociation $locfldr/radiants/temp/* -c ${locfldr}/config/uk0006/.config -p gist_ncar
$fils=(get-item "${locfldr}/radiants/temp/UK*").Name
foreach($fil in $fils){
    $newn=$fil.replace("UK002F","ALLCAM")
    move-item ${locfldr}/radiants/temp/${fil} ${locfldr}/radiants/${newn} -force
}
Remove-Item ${locfldr}/radiants/temp/*.txt
set-location $loc
