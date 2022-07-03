# simple script to copy then display the most recent CMN/RMS meteor captures
# if RMS is installed it will also run some postprocessing to generate
# shower maps, JPGs and a UFO-Orbit-compatible detection file

$loc = get-location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    $inifname = 'radiostation.ini'
}else {
    $inifname = $args[0]
}

$ini=get-inicontent $inifname
$hostname=$ini['detectionpi']['hostname']
$localfolder=$ini['detectionpi']['localfolder']
$remotefolder=$ini['detectionpi']['remotefolder']
$pyenv=$ini['detectionpi']['pyenv']
$srcloc=$ini['detectionpi']['srcloc']

if ((test-path $localfolder) -eq 0) { mkdir $localfolder}
if ((test-path $localfolder\Archive) -eq 0) { mkdir $localfolder\Archive}
if ((test-path $localfolder\Junk) -eq 0) { mkdir $localfolder\Junk}

# copy the latest data from the Pi
$remotepath=$hostname+':'+$remotefolder
$localpath='/mnt/'+$localfolder.substring(0,1)+$localfolder.substring(2)

ssh astro2 "touch $srcpath/Captures/lastsync.txt"
bash -c "rsync -avz --delete --ignore-errors $remotepath/ $localpath --exclude Junk --exclude Archive"

# find the latest set of data on the local drive
$destpath=$localfolder+'\Captures'
$path=(get-childitem $destpath -directory | sort-object creationtime | select-object -last 1).name
$myf = $destpath + '\' + $path

$env:pythonpath="$srcloc/src"
conda activate $pyenv
write-output $myf $localfolder
python $srcloc/src/analyse_detection.py $myf -o $localfolder --flipped 

$remotepath=$hostname+':'+$remotefolder
ssh $hostname "cd $remotefolder/Captures && find . -type f -newer ./lastsync.txt" > $localfolder/newer.txt
bash -c "rsync -avz -include-from=$localfolder/newer.txt $remotepath/Captures $localpath/captures"
bash -c "rsync -avz --delete --ignore-errors $localpath/ $remotepath --exclude Junk --exclude Archive --exclude Logs --exclude runlogs"

set-location $loc