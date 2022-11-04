#
# script to get livestream including bad and fireballs
#

$curloc = get-location
set-location $PSScriptRoot

# load the helper functions
. .\helperfunctions.ps1

# read the inifile
$ini=get-inicontent 'live.ini'
$awsprofile = $ini['live']['awsprofile']
$remotefolder=$ini['live']['remotefolder'] 
$localfolder=$ini['live']['localfolder'] 
$remotebad=$ini['live']['remotebad'] 
$badfolder=$ini['live']['badfolder'] 
$fbfolder=$ini['live']['fbfolder'] 
$ffmpeg=$ini['live']['ffmpeg'] 
$fbonly=$ini['live']['fbonly'] 
$convfb=$ini['live']['convertfbs'] 


if ($fbonly -eq 'False') 
{
    aws s3 sync $remotefolder $localfolder --exclude "*" --include "*.jpg" --include "*.xml" --include "*.csv" --exclude "*temp*" --profile $awsprofile
    aws s3 sync $remotebad $badfolder --exclude "*" --include "*.jpg" --include "*.xml" --exclude "*temp*" --profile $awsprofile
    aws s3 sync $remotefolder $fbfolder --exclude "*" --include "*.mp4" --exclude "*temp*" --profile $awsprofile
}else {
    $mthtoget=read-host -prompt 'Enter month to retrieve eg 202007'
    $incl='M' + $mthtoget + '*.mp4'
    Write-Output "getting MP4s for $incl"
    aws s3 sync $remotefolder $fbfolder --exclude "*" --include $incl --exclude "*temp*"
    if ($convfb -eq 'True') 
    {
        Write-Output "converting to AVI"
        set-location $fbfolder
        set-location mp4s
        $flist=(Get-ChildItem $incl)
        for($i=0;$i -lt $flist.count ; $i++ ){
            $fn=$flist[$i].basename
            $mp4=$fn+'.mp4'
            $avi=$fn+'.avi'
            if((test-path ..\$avi) -eq $false){
                write-output 'new file $avi'
                & $ffmpeg -i $mp4 -vframes 300 -q:v 0 ..\$avi
            }
        }
    }
}
Write-Output "Done"
set-location $curloc
pause