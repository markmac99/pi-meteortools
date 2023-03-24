# Copyright (C) Mark McIntyre
$loc=get-location
$env:pythonpath="e:\dev\meteorhunting\rms;e:\dev\meteorhunting\westernmeteorpylib;e:\dev\meteorhunting\ukmon-shared\ukmon_pylib"
$myf=(get-location).path
$path=$myf.split('\')[-1]
$ftpfil=$myf+'\FTPdetectinfo_'+$path+'.txt'
$hostname=$path.substring(0,6)

if ((test-path *track_stack.jpg) -eq 0)
{
    Write-Output "creating image"
    conda activate RMS
    set-location e:\dev\meteorhunting\RMS
    python -m Utils.TrackStack $myf -c $myf\.config -x
    set-location $loc
}

$li = (get-content $ftpfil | select-object -first 1)
$metcount = [int]$li.split(' ')[3]
$ts=(Get-ChildItem $myf\*track_stack.jpg).name
$ymd=$ts.substring(7,8)

Write-Output "Annotating image, cam is $hostname, date is $ymd, metcount is $metcount"
$env:pythonpath="e:\dev\meteorhunting\rms;e:\dev\meteorhunting\westernmeteorpylib;e:\dev\meteorhunting\ukmon-shared\ukmon_pylib"
python -m utils.annotateImage $myf\$ts $hostname $metcount $ymd
Write-Output "copying image"
$newn=$ts.substring(0,15)+".jpg"
copy-item $myf\*track_stack.jpg f:\videos\meteorcam\trackstacks\$newn
