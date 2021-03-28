# powershell script to backup the meteorcam data

$src='C:\Users\mark\Videos\astro\MeteorCam'
$dest='g:\astrovideo\meteorcam'
$cl='ne','tc','uk0006'

$CurrentDate = Get-Date
$daysback=-190
$DatetoDelete = $CurrentDate.AddDays($Daysback)

$yr = [int](get-date -uformat '%Y')
$syr=$yr-1

foreach ($cam in $cl)
{
    for ($i=$syr; $i -le $yr; $i++ )
    {
        $ssrc=$src+'\'+$cam+'\'+$i
        $sdest=$dest+'\'+$cam+'\'+$i 
        echo $ssrc $sdest
        robocopy $ssrc $sdest *.csv *.jpg *.bmp *.txt *.xml M*.avi /dcopy:DAT /m /v /s /z /r:3
        Get-ChildItem $ssrc -Recurse | Where-Object { $_.LastWriteTime -lt $DatetoDelete } | Remove-Item -recurse
    }
}
$flds='archive','BatsAndBirds','Fireballs','Docs','OtherCameras','Programmes','radio','scripts','sprites','stacks','stills'
foreach ($fld in $flds)
{
    $ssrc=$src+'\'+$fld
    $sdest=$dest+'\'+$fld
    robocopy $ssrc $sdest *.ps1 *.py *.bat *.sh *.csv *.jpg *.bmp *.txt *.xml M*.avi /dcopy:DAT /m /v /s /z /r:3
}
