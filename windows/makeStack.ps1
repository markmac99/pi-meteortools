# script to push video data to the website

set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1

# read the inifile
$inifname='stacking.ini'

$ini=get-inicontent $inifname
$localfolder=$ini['stacking']['localfolder']
$targetfolder=$ini['stacking']['targetfolder']

$fnam=$args[0]
$minbri=$args[1]

if($args.count -lt 1) {$fnam='stack.jpg'}
if($args.count -lt 2) {$minbri=0.5}

$targ=$targetfolder+'\'+$fnam
.\stacker.exe $localfolder jpg $minbri $targ

& 'C:\Program Files (x86)\FastStone Image Viewer\fsviewer.exe' $targ
$del = read-host -Prompt 'Delete source files?'

if ( $del -eq 'Y' -or $del -eq 'y' )
{
    set-location $localfolder
    remove-item *.jpg
}

set-location $psscriptroot