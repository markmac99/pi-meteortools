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
$rdt=[datetime]($ym.substring(0,4)+'-'+$ym.substring(4))
$prevym = ($rdt.addmonths(-1)).tostring('yyyyMM')

$srcpath=$localfolder + '\ConfirmedFiles'
$destpath=$localfolder+'\..\mthlystacks\'+$hostname

if ((test-path $destpath) -eq 0) { mkdir $destpath}

$ffpatt = 'FF*' + $prevym + '*.fits'
Remove-Item $destpath\$ffpatt

$dlist = (Get-ChildItem  -directory "$srcpath\*_$ym*" ).name
foreach ($path in $dlist) {
    robocopy $srcpath\$path $destpath FF*.fits mask.bmp flat.bmp /NFL /NDL /NJH /NJS /nc /ns /np /v
}

conda activate $RMS_ENV
set-location $RMS_LOC
python -m Utils.StackFFs $destpath -x -s -b jpg -f $destpath/flat.bmp -m $destpath/mask.bmp

$stackfile = (Get-ChildItem  $destpath\*.jpg ).name
if ((test-path $destpath\$stackfile) -eq 1)
{
    $metcount = $stackfile.split('_')[2]
    $imgfile=("$destpath\$stackfile").replace('\','/')
    python -c "from ukmon_meteortools.utils import annotateImage; annotateImage('$imgfile', '$hostname', $metcount, '$ym')"
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
set-location $loc
#pause