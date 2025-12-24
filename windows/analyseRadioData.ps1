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
$processed = get-content "${env:mrdatadir}/../processed.txt"
$flist=(Get-ChildItem .\radar_data\Captures\ -r )
foreach ($i in $flist) {
    $fullname = $i.fullname
    if (test-path $fullname -pathtype leaf) # only process files
    {
        $name = $i.name 
        if ( -not ($processed -imatch "$name" )) 
        {
            python C:\dev\meteorhunting\pi-meteortools\radio\getStats.py $fullname
        }
    }
}
set-location $here
