# powershell script to analyse my radio data

$here = get-location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini = get-inicontent archive.ini
$radarloc = $ini['local']['RADIODATA']
set-location "$radarloc"
bash -c "rsync -avz --delete radiopi:radar_data/Captures/ ./radar_data/Captures/"
bash -c "rsync -avz --delete radiopi:radar_data/Logs/ ./radar_data/Logs/"

conda activate vMeteorRadio
$env:mrdatadir="$radarloc/radar_data"
$flist=(Get-ChildItem .\radar_data\Captures\ -r )
foreach ($i in $flist) {
    $fullname = $i.fullname
    if (test-path $i -pathtype leaf)
    {
        $name = $i.name 
        $imgname=$name.replace('Captures','Images').replace('SMP','PSD').replace('npz','png')
        $imgname=".\radar_data\Images\" + $imgname
        if (test-path $imgname -pathtype leaf){
            Write-Output "skipping creation of $i"
        }else {
            python C:\dev\meteorhunting\MeteorRadio\src\analyse_detection.py -s -n -3 --colour PuBu -a $fullname
        }
    }
}
$flist=(Get-ChildItem .\radar_data\Captures\)
foreach ($i in $flist) {
    $fullname = $i.fullname
    Write-Output $fullname
    python C:\dev\meteorhunting\pi-meteortools\radio\getStats.py $fullname
}
set-location $here
