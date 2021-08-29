# simple script to copy then display the most recent CMN/RMS meteor captures
# if RMS is installed it will also run some postprocessing to generate
# shower maps, JPGs and a UFO-Orbit-compatible detection file

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
$maxage=$ini['camera']['maxage']
$localfolder=$ini['camera']['localfolder']
$binviewer_exe_loc=$ini['python']['binviewer_exe_loc']
$binviewer_pyt_loc=$ini['python']['binviewer_pyt_loc']
$binviewer_env=$ini['python']['binviewer_env']
$USE_EXE=$ini['python']['USE_EXE']
$RMS_INSTALLED=$ini['rms']['rms_installed']
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']

# copy the latest data from the Pi
$srcpath='\\'+$hostname+'\RMS_data\ArchivedFiles'
$destpath=$localfolder+'\ArchivedFiles'
if ((test-path $destpath) -eq 0) { mkdir $destpath}
$age=[int]$maxage
robocopy $srcpath $destpath /dcopy:DAT /tee /v /s /r:3 /maxage:$age /xf *.bz2

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
set-location $PSScriptRoot
$regex="userej"
switch -regex -file $bcfg { 
    $regex { 
        $tst=($_.split('=')[1]).trim()
        if ($tst -eq "1"){
            .\uploadToCmnRejected.ps1 $myf
        } 
    }
}

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
            python -m Utils.ShowerAssociation $ftpfil -x
            python -m Utils.StackFFs $myf -x -b jpg -f $myf\flat.bmp -m $myf\mask.bmp
            python -m Utils.TrackStack $myf -c $myf\.config
            python -m Utils.BatchFFtoImage $myf jpg -t
            $allplates = $localfolder + '\ArchivedFiles\' + $path + '\platepars_all_recalibrated.json'
            copy-item $allplates $destpath
        }
        else{
            write-output skipping' '$myf
        }
    }    
}
set-location $PSScriptRoot
$dtstr=((get-date).adddays(-1)).tostring('yyyyMMdd')
.\getPossibles $inifname $dtstr

# .\reorgByYMD.ps1 $args[0]
# .\UploadToUkMon.ps1 $args[0]

