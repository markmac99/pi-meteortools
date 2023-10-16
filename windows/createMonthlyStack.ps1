# Copyright (C)Mark McIntyre
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
$ini=get-inicontent $inifname
$remotepth=$ini['camera']['hostname']
$localfolder=$ini['camera']['localfolder']
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']
$webserver=$ini['website']['webserver']
$awsprofile=$ini['mjmm']['awsprofile']
$awsbuck=$ini['mjmm']['cambucket']

$hostname=(split-path $remotepth -leaf)

if ($args.count -eq 2){
    $ym = ([string]$args[1]).substring(0,6)
}else {
    $ym = (get-date -uformat '%Y%m')
}

$srcpath=$localfolder + '\ArchivedFiles'
$destpath=$localfolder+'\..\mthlystacks\'+$hostname

if ((test-path $destpath) -eq 0) { mkdir $destpath}

Get-ChildItem $destpath\*.fits -exclude "FF_${hostname}_${ym}*" | Remove-Item
remove-item $destpath\*.jpg

# for the current month we can fetch from the camera
$currmth = (get-date -uformat '%Y%m')
if ($ym -eq $currmth ) {
  $upstreampath='\\' + $hostname + '\RMS_data\tmpstack\'
  robocopy $upstreampath $destpath FF*.fits mask.bmp flat.bmp /NFL /NDL /NJH /NJS /nc /ns /np /xc /xo /v /purge
}
else {
    $dlist = (Get-ChildItem  -directory "$srcpath\*_$ym*" ).name
    foreach ($path in $dlist) {
        robocopy $srcpath\$path $destpath FF*.fits mask.bmp flat.bmp /NFL /NDL /NJH /NJS /nc /xc /ns /np /v
    }
}

conda activate $RMS_ENV
set-location $RMS_LOC
python -m Utils.BatchFFtoImage $destpath jpg

$fitsfiles=(Get-ChildItem  $destpath\*.fits).fullname
& explorer $destpath.replace('/','\')
pause

foreach ($fits in $fitsfiles) {
    $jpg = $fits.replace('.fits','.jpg')
    if ((test-path $jpg) -eq 0) { remove-item "$fits" }
}
python -m Utils.StackFFs $destpath -x -s -b jpg -f $destpath/flat.bmp -m $destpath/mask.bmp

$stackfile = (Get-ChildItem  $destpath\*stack*.jpg ).name
if ((test-path $destpath\$stackfile) -eq 1)
{
    $metcount = $stackfile.split('_')[2]
    $imgfile=("$destpath\$stackfile").replace('\','/')
    python -c "from meteortools.utils import annotateImage; annotateImage('$imgfile', '$hostname', $metcount, '$ym')"
    $newname=$hostname.toupper() + '_' + $ym + '.jpg'
    Move-Item $destpath\*.jpg $destpath\..\$newname -force

    set-location "$destpath\.."
    $latf=$hostname.toupper() + '_latest.jpg'
    $webtarg=$webserver+":data/meteors"
    scp $newname $webtarg/$latf
    $webtarg = $awsbuck + '/' + $hostname.toupper() + "/stacks/" 
    aws s3 cp $newname $webtarg --profile $awsprofile
}
else {
    Write-Output 'no stack to upload'
}
#if processing the current month sync the local cleaned folder back to the tempdir on the target
if ($ym -eq $currmth ) {
  $upstreampath='\\' + $hostname + '\RMS_data\tmpstack\'
  Write-Output "$upstreampath"
  robocopy $destpath $upstreampath FF*.fits mask.bmp flat.bmp /NFL /NDL /NJH /NJS /nc /ns /xc /np /v /purge
}

set-location $loc
#pause