# script to backup a month's worth of meteorcam data to an SD card
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    write-output "ini file missing, can't continue"
    exit 1
}
$inifname = "uk0006.ini"
$ini=get-inicontent $inifname
$localfolder=$ini['camera']['localfolder']

$ym=$args[0]
$targ=$args[1]

$locd = $localfolder.substring(0,2)
$localpth = $localfolder.substring(2, $localfolder.length-8)
$remfldr = ${targ} + $localpth

$cams=@('UK0006','UK000F','UK001L','UK002F')
foreach ($cam in $cams){
    robocopy ${locd}${localpth}\${cam}\ArchivedFiles ${remfldr}\${cam}\archivedfiles FTPdetectinfo_${cam}_${ym}*.txt /s
    robocopy ${locd}${localpth}\${cam}\ArchivedFiles ${remfldr}\${cam}\archivedfiles platepars* /s
    robocopy ${locd}${localpth}\${cam}\MLChecks ${remfldr}\${cam}\MLChecks /s
}