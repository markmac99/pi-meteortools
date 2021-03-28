# powershell script to grab interesting files from Pi which were 
# not picked up by the automated process for some reason but 
# which you would like to examine. 
# The script takes two parameters
#   grabInterestingFiles.ps1 uk0006.ini 20200619_023417
# the camera config file and date/time you want
# The datetime does not need to be exact, the script grabs files from +/- 20 seconds
# around the target. The files are converted to JPG so you can easily check them.

set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    write-output "Usage: grabInterestingFiles.ps1 UK0006.ini yyyymmdd_hhmmss"
    exit 1
}
$inifname = $args[0]
if ((test-path $inifname) -eq $false) {
    write-output "ini file missing or invalid, can't continue"
    exit 1
}
$ini=get-inicontent $inifname

$hostname=$ini['camera']['hostname']
#$remotefolder=$ini['camera']['remotefolder']
$localfolder=$ini['camera']['localfolder']
$camera_name=$ini['camera']['camera_name']
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']

# datetime of interest in YYYYMMDD_HHMMSS  format
$dtim=[datetime]::parseexact($args[1],'yyyyMMdd_HHmmss', $null)
# data is stored in a folder based on start time.
# so captures after midnight are stored in the prior days folder
$ftim = $dtim
if ($dtim.hour -lt 13 )
{
    $ftim=$dtim.adddays(-1)
}
$srcpath='\\'+$hostname+'\RMS_Share\CapturedFiles\'+$camera_name+'_'+$ftim.tostring('yyyyMMdd')+'*'
$srcpath=(get-childitem $srcpath).fullname

$destpath=$localfolder+'/Interesting/'+$ftim.tostring('yyyyMMdd')
if (-not (test-path $destpath)) {mkdir $destpath | out-null}

write-output "looking in $srcpath"
write-output "saving to $destpath"
$dtim=$dtim.AddSeconds(-20)
for ($i = 0; $i -lt 6; $i++)
{
    $dstr=$dtim.ToString('yyyyMMdd_HHmmss')
    $dstr=$dstr.substring(0,14)+'*.fits'
    $fnam=$srcpath+'\FF_'+$camera_name+'_'+$dstr
    #write-output $fnam
    copy-item $fnam $destpath
    $dtim=$dtim.addseconds(10)
}
set-location $rms_loc
conda activate $rms_env
python -m Utils.BatchFFtoImage $destpath jpg
set-location $curloc
explorer $destpath.replace('/','\')