# simple script to copy then display the most recent CMN/RMS meteor captures
# if RMS is installed it will also run some postprocessing to generate
# shower maps, JPGs and a UFO-Orbit-compatible detection file
# Copyright (C) Mark McIntyre

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
$maxage=$ini['camera']['maxage']
$localfolder=$ini['camera']['localfolder']
$binviewer_exe_loc=$ini['python']['binviewer_exe_loc']
$binviewer_pyt_loc=$ini['python']['binviewer_pyt_loc']
$binviewer_env=$ini['python']['binviewer_env']
$USE_EXE=$ini['python']['USE_EXE']
$RMS_INSTALLED=$ini['rms']['rms_installed']
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']
$upload_rej=$ini['cleaning']['uploadtogmn']
$pylib=$ini['ukmon']['ukmon_pylib']
$hostname=(split-path $remotepth -leaf)

# copy the latest data from the Pi or other location
if ($remotepth -ne $hostname ) {
    $srcpath='\\'+$remotepth+'\ArchivedFiles'
}
else{
    $srcpath='\\'+$remotepth+'\RMS_data\ArchivedFiles'
}

$destpath=$localfolder+'\ArchivedFiles'
if ((test-path $destpath) -eq 0) { mkdir $destpath}
$age=[int]$maxage
robocopy $srcpath $destpath /dcopy:DAT /tee /v /s /r:3 /maxage:$age /xf *.bz2

# purge older logfiles
$Days = "30" 
$CutoffDate = (Get-Date).AddDays(-$Days) 
$logpath = $localfolder + '/logs'
Get-ChildItem -Path $logpath -Recurse -File | Where-Object { $_.LastWriteTime -lt $CutoffDate } | Remove-Item –Force

# find the latest set of data on the local drive
$path=(get-childitem $destpath -directory | sort-object creationtime | select-object -last 1).name
$myf = $destpath + '\'+$path

# Use the Python version of binviewer, or the compiled binary?
if ($USE_EXE -eq 1){
    set-location $binviewer_exe_loc
    & .\CMN_binviewer.exe $myf -c | out-null
    $bcfg = $binviewer_exe_loc + "/config.ini"
}
else {
    conda activate $binviewer_env
    set-location $binviewer_pyt_loc
    python CMN_BinViewer.py $myf -c
    $bcfg = $binviewer_pyt_loc + "/config.ini"
}

# get the FR files
Write-Output "Copying mp4 and FR files where available"
$conff = $localfolder+'\ConfirmedFiles\' + $path
$fflist=(Get-ChildItem $conff\FF*.fits).name
if ($fflist.count -gt 0)
{
    $frlist=$fflist.replace('FF_','FR_').replace('.fits','.bin')
    foreach ($frfile in $frlist)
    {
        $srcfile = $srcpath + '/'+ $path + '/' + $frfile
        $srcfile = $srcfile.replace('/','\')
        if ((test-path $srcfile) -eq 1){
            Copy-Item "$srcfile" "$conff"
        }
    }
    $mp4list=$fflist.replace('.fits','.mp4')
    foreach ($mp4file in $mp4list)
    {
        $srcfile = $srcpath + '/'+ $path + '/' + $mp4file
        $srcfile = $srcfile.replace('/','\')
        if ((test-path $srcfile) -eq 1){
            Copy-Item "$srcfile" "$conff"
        }
    }
}else {
    write-output "No FF/FR files today"
}

set-location $PSScriptRoot
$regex="userej"
switch -regex -file $bcfg { 
    $regex { $tst=($_.split('=')[1]).trim()  } 
}

if ($tst -eq "1" -and $upload_rej -eq "True"){
    .\uploadToCmnRejected.ps1 $myf
}
else {
    write-output "Skipping GMN ML upload"
}
# decide whether to do the trackstack
$uploadts = $ini['mjmm']['uploadtrackstacks']
$uploadts = $ini['mjmm']['uploadmthlystacks']

$env:pythonpath=$pylib
# switch RMS environment to do some post processing
if ($RMS_INSTALLED -eq 1){
    # reprocess the ConfirmedFiles folder to generate JPGs, shower maps, etc
    conda activate $RMS_ENV
    set-location $RMS_LOC
    $mindt = (get-date).AddDays(-$age)

    $destpath=$localfolder+'\ConfirmedFiles'
    $dlist = (Get-ChildItem  -directory $destpath | Where-Object { $_.creationtime -gt $mindt }).name
    foreach ($path in $dlist) {
        $myf = $destpath + '\'+$path
        $ftpfil=$myf+'\FTPdetectinfo_'+$path+'.txt'
        $radfil=$myf+'\'+$path+'_radiants.png'

        $ftpexists=test-path $ftpfil
        $radexists=test-path $radfil

        if ($ftpexists -ne 0 -and $radexists -eq 0 ){
            $mask = $localfolder + '\ArchivedFiles\' + $path + '\mask.bmp'
            $flat = $localfolder + '\ArchivedFiles\' + $path + '\flat.bmp'
            copy-item $mask $myf
            copy-item $flat $myf
            python -m Utils.ShowerAssociation $ftpfil -x -p gist_ncar -c $myf\.config
            python -m Utils.StackFFs $myf -x -b jpg -f $myf\flat.bmp -m $myf\mask.bmp
            python -m Utils.BatchFFtoImage $myf jpg -t
            $allplates = $localfolder + '\ArchivedFiles\' + $path + '\platepars_all_recalibrated.json'
            copy-item $allplates $destpath

            if ($uploadts -eq 1 ) {
                python -m Utils.TrackStack $myf -c $myf\.config -x --constellations -b
                $li = (get-content $ftpfil | select-object -first 1)
                $metcount = [int]$li.split(' ')[3]
                $ts=(Get-ChildItem $myf\*track_stack.jpg).name
                if ($ts.count -ne 0){
                    $ymd=$ts.substring(7,8)
                    $imgfile=("$myf\$ts").replace('\','/')
                    python -c "from meteortools.utils import annotateImage; annotateImage('$imgfile', '$hostname', $metcount, '$ymd')"
                    $newn=$ts.substring(0,15)+".jpg"
                    copy-item $myf\*track_stack.jpg $localfolder\..\trackstacks\$newn
                }else {
                    write-output "No trackstack today"
                }
            }
        }
        else{
            write-output "skipping $myf"
        }
    }    
}
set-location $PSScriptRoot
if ($uploadms -eq 1 ) {
    .\createMonthlyStack.ps1 $inifname $path.substring(7,8)
}
# upload to my website, if appropriate
if ($uploadts -eq 1 ) {
    .\uploadTrackStacks.ps1 $inifname 
}

