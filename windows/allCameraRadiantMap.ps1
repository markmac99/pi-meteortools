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
    $bftpfil = 'c:/temp/' + (split-path $ftpfil -leaf)

    copy-item $ftpfil c:\temp\
    $ftplist = $ftplist + $bftpfil
}
$cfg = $srcpath + '/' + $dlist + '/.config'
Set-Location $rms_loc
conda activate $rms_env
python -m Utils.ShowerAssociation $ftplist[0] $ftplist[1] $ftplist[2] $ftplist[3] -x -c $cfg
foreach ($fil in $ftplist)
{
    remove-item $fil
}
$targpth=$localfolder + '\..\radiants'
if ((test-path $targpth) -eq 0 ) {mkdir $targpth }

$radpng = (Get-ChildItem  "c:\temp\*$dt1*radiants.png" ).name
$newfname = 'ALLCAM'+ $radpng.substring(6,$radtxt.length-6)
Move-Item "c:\temp\$radpng" "$targpth\$newfname" -force
$radtxt = (Get-ChildItem  "c:\temp\*$dt1*radiants.txt" ).name
$newfname = 'ALLCAM'+ $radtxt.substring(6,$radtxt.length-6)
move-item "c:\temp\$radtxt" "$targpth\$newfname" -force 

set-location $loc
