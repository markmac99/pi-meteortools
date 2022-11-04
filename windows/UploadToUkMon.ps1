#daily upload of UFO or RMS data to the UKMON archive

$curloc=get-location
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

$ukmon_member=$ini['ukmon']['ukmon_member']
$awsprofile=$ini['aws']['awsprofile']
$localfolder=$ini['camera']['localfolder']
$UFO=$ini['camera']['UFO']

# for this to be useable you must be a UKMON contributor 
# contact us on Facebook to start contributing! 

$ismember=$UKMON_member
if ($ismember -eq 'Yes')
{
    $yr = (get-date).tostring("yyyy")
    $ym = (get-date).tostring("yyyyMM")
    $ym2 = (get-date).addmonths(-1).tostring("yyyyMM")
    $ym3 = (get-date).addmonths(-2).tostring("yyyyMM")

    $srcpath=$localfolder+'/'+$yr+'/' + $ym + '/'

    write-output "Syncing $srcpath"
    $targ= 's3://ukmon-shared/archive/' + $ukmoncam  + '/' + $yr+'/' + $ym + '/'

    if ($UFO -eq 0){
        aws s3 sync $srcpath $targ --include * --exclude *.fits --exclude *.bin --exclude *.gif  --exclude *.bz2 --exclude UK*.mp4 --profile $awsprofile
    } else {
        aws s3 sync $srcpath $targ --exclude * --include *.csv --include *P.jpg --include *.txt --include *.xml --include *.json --exclude *detlog.csv  --profile $awsprofile
    }
    if ($ym2 -ne $ym){ 

        $srcpath=$localfolder+'/'+$yr+'/' + $ym2 + '/'
        write-output "Syncing $srcpath"
        $targ= 's3://ukmon-shared/archive/' + $ukmoncam  + '/' + $yr+'/' + $ym2 + '/'
        if ($UFO -eq 0){
            aws s3 sync $srcpath $targ --include * --exclude *.fits --exclude *.bin --exclude *.gif  --exclude *.bz2 --exclude UK*.mp4  --profile $awsprofile
        } else {
            aws s3 sync $srcpath $targ --exclude * --include *.csv --include *P.jpg --include *.txt --include *.xml --include *.json --exclude *detlog.csv  --profile $awsprofile
        }
    }
    if ($ym3 -ne $ym2){ 

        $srcpath=$localfolder+'/'+$yr+'/' + $ym3 + '/'
        write-output "Syncing $srcpath"
        $targ= 's3://ukmon-shared/archive/' + $ukmoncam  + '/' + $yr+'/' + $ym3 + '/'
        if ($UFO -eq 0){
            aws s3 sync $srcpath $targ --include * --exclude *.fits --exclude *.bin --exclude *.gif  --exclude *.bz2 --exclude UK*.mp4  --profile $awsprofile
        } else {
            aws s3 sync $srcpath $targ --exclude * --include *.csv --include *P.jpg --include *.txt --include *.xml --include *.json --exclude *detlog.csv  --profile $awsprofile
        }
    }

    Write-Output 'checked and uploaded any new files'
}
else {
    Write-Output 'check ini file to make sure ukmon details are set'
    Write-Output 'as this script will only work if you are set up as a contributor'
}
set-location $curloc