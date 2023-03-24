# Copyright (C) Mark McIntyre
$loc = get-location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile

$dt1 =$args[0]
if ($args.count -gt 1){
    $dt2=$args[1]
}else {
    $dt2=$dt1
}

$camlist = @('uk0006','uk000f','uk001l','uk002f')

$ftplist=@()
$startdt = [datetime]::parseexact($dt1,'yyyyMMdd', $null)
$enddt = [datetime]::parseexact($dt2,'yyyyMMdd', $null)


while ($startdt -le $enddt){
    $dt1=$startdt.tostring('yyyyMMdd')
    for ($i=0;$i -lt $camlist.count ; $i++) { 
        $inifname =$camlist[$i]+ ".ini"
        $ini=get-inicontent $inifname
        $localfolder=$ini['camera']['localfolder']
        $rms_loc=$ini['rms']['rms_loc']
        $rms_env=$ini['rms']['rms_env']
        $srcpath=$localfolder + '\ConfirmedFiles'
        $datedir=$srcpath + '\*_' + $dt1 + "_*" 
        $dlist = (Get-ChildItem  -directory "$datedir" ).name
        $ftpfil=$srcpath + '\' + $dlist + '\FTPdetectinfo_' + $dlist + '.txt'
        $bftpfil = $targpth +'\tmp\' + (split-path $ftpfil -leaf)
        $targpth=$localfolder + '\..\radiants'
        if ((test-path $ftpfil) -ne 0 ) {
            copy-item $ftpfil "$targpth\tmp\"
            $ftplist = $ftplist + $bftpfil
        }
    }
    $startdt = $startdt.adddays(1)
}
$cfg = $srcpath + '/' + $dlist + '/.config'
Set-Location $rms_loc
conda activate $rms_env
python -m Utils.ShowerAssociation "$targpth\tmp\*" -x -c $cfg  -p gist_ncar
if ((test-path $targpth) -eq 0 ) {mkdir $targpth }

$radpng = (Get-ChildItem  "$targpth\tmp\*$dt1*radiants.png" ).name
$newfname = 'ALLCAM'+ $radpng.substring(6,$radpng.length-6)
Move-Item "$targpth\tmp\$radpng" "$targpth\$newfname" -force
Write-Output "created $newfname"
$radtxt = (Get-ChildItem  "$targpth\tmp\*$dt1*radiants.txt" ).name
$newfname = 'ALLCAM'+ $radtxt.substring(6,$radtxt.length-6)
move-item "$targpth\tmp\$radtxt" "$targpth\$newfname" -force 
remove-item "$targpth\tmp\*"

set-location $loc
