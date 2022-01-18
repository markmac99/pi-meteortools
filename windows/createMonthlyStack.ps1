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
$ini=get-inicontent $inifname
$hostname=$ini['camera']['hostname']
$localfolder=$ini['camera']['localfolder']
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']

if ($args.count -eq 2){
    $ym = [int]$args[1]
}else {
    $ym = (get-date -uformat '%Y%m')
}

$srcpath=$localfolder + '\ConfirmedFiles'
$destpath=$localfolder+'\..\mthlystacks\'+$hostname

if ((test-path $destpath) -eq 0) { mkdir $destpath}

if((get-date -uformat '%d') -eq '01')
{
    Remove-Item $destpath\FF*.fits
}
$dlist = (Get-ChildItem  -directory "$srcpath\*_$ym*" ).name
foreach ($path in $dlist) {
    robocopy $srcpath\$path $destpath FF*.fits mask.bmp flat.bmp /NFL /NDL /NJH /NJS /nc /ns /np
}

conda activate $RMS_ENV
set-location $RMS_LOC
python -m Utils.StackFFs $destpath -x -s -b jpg -f $destpath/flat.bmp -m $destpath/mask.bmp

$stackfile = (Get-ChildItem  $destpath\*.jpg ).name
if ((test-path $destpath\$stackfile) -eq 1)
{
    $metcount = $stackfile.split('_')[2]
    python -m utils.annotateImage $destpath\$stackfile $hostname $metcount
    $newname=$hostname.toupper() + '_' + $ym + '.jpg'
    Move-Item $destpath\*.jpg $destpath\..\$newname -force

    $webserver="wordpresssite"
    set-location "$destpath\.."
    $latf=$hostname.toupper() + '_latest.jpg'
    $webtarg=$webserver+":data/meteors"
    scp $newname $webtarg/$latf
    $webtarg=$webserver+":data/mjmm-data/" + $hostname.toupper() + "/stacks"
    scp $newname $webtarg
}
set-location $loc