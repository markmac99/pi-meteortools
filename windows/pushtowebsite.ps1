# script to push video data to the website
$curloc = get-location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1

# read the stacking inifile
$inifname='stacking.ini'
$ini=get-inicontent $inifname

$cams=($ini['cameras']['cams']).split(',')
$tempfolder=$ini['stacking']['tmpfolder']

$sitename=$ini['website']['sitename']
$userid=$ini['website']['userid']
$targetdir=$ini['website']['targetdir']
if ($env:username -eq 'admin' )
{
    $key=$ini['website']['admkey']
}else{
    $key=$ini['website']['usrkey']
}

$yr=(get-date -uformat '%Y')
$mth=(get-date -uformat '%Y%m')

for ($i=0; $i -lt $cams.length ; $i ++)
{
    $cam=$cams[$i]

    $msg='Collecting '+$cam+' data'
    write-output $msg
    $inifname=$cam+'.ini'
    $ini=get-inicontent $inifname
    $localfolder=$ini['camera']['localfolder']
    $isufo=$ini['camera']['ufo']
    $pref='FF'
    $suff='.jpg'
    if ($isufo -eq 1){
        $suff='p.jpg'
        $pref='M'
    }
    
    remove-item $tempfolder\*.jpg
    $x=(get-childitem -r $localfolder\$yr\$mth\$pref*$suff).fullname
    for ($j=0;$j -lt $x.count ; $j++) 
        {copy-item $x[$j] $tempfolder }
    $ofname = $cam+'_latest.jpg'

    .\stacker.exe $tempfolder.replace('/','\') jpg 0.4 $tempfolder\$ofname
    set-location $tempfolder 
    $website=$userid+'@'+$sitename+':'+$targetdir
    scp -o StrictHostKeyChecking=no -i $key $ofname $website    
    set-location $PSScriptRoot
}

set-location $curloc