#
# upload trackstacks to website
#

$loc = get-location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1

if ($args.count -eq 0) {
    write-output "ini file missing, can't continue"
    exit 1
}
$inifname = $args[0]
$ini=get-inicontent $inifname
$hostname=$ini['camera']['hostname']
$localfolder=$ini['camera']['localfolder']
$pylib=$ini['ukmon']['ukmon_pylib']


if ($args.count -eq 2){
    $ymd = [int]$args[1]
}else {
    $ymd = (get-date).adddays(-1).tostring('yyyyMMdd')
}

$cnfpath=$localfolder + "\ConfirmedFiles\$hostname" + "_$ymd" +"*\FTPdetectinfo*.txt"
$ftps = (get-childitem $cnfpath).FullName
if ($ftps.count -eq 0 ) { 
    write-output 'no data for today'
}
else {
    $theftp = ($ftps -notlike '*confirmation*')
    $li = (get-content $theftp | select-object -first 1)
    $metcount = [int]$li.split(' ')[3]
    
    $srcpath=$localfolder + '\..\trackstacks\'
    #$destpath=$localfolder+'\..\tmpstack\'
    
    $fnam = "$srcpath$hostname" + "_$ymd" + "*track_stack.jpg"
    
    $stackfile = (Get-ChildItem  $fnam ).Name
    
    if ($stackfile.length -ne 0)
    {
        $hnu = $hostname.toupper()
        $newname=$hnu + '_' + $ymd + '.jpg'
        Rename-Item $srcpath\$stackfile $newname
        $env:pythonpath=$pylib
        python -m utils.annotateImage $srcpath\$newname $hostname $metcount $ymd
        $dirname = "s3://mjmm-data/" + $hnu + "/trackstacks/"
        . $ini['website']['awskey']
        aws s3 sync $srcpath $dirname --exclude "*" --include "$hnu*"
    }
    else
    {
        $cnfpath = $localfolder + "\ConfirmedFiles\"
        $ofnam =  "$cnfpath$hostname" + "_$ymd*\" + "*track_stack.jpg"
        $stackfile = (Get-ChildItem  $ofnam ).fullName
        if ($stackfile.length -ne 0)
        {
            $hnu = $hostname.toupper()
            $newname=$hnu + '_' + $ymd + '.jpg'
            copy-Item $stackfile $srcpath\$newname -Force
            $env:pythonpath=$pylib
            python -m utils.annotateImage $srcpath\$newname $hostname $metcount $ymd
            $dirname = "s3://mjmm-data/" + $hnu + "/trackstacks/"
            . $ini['website']['awskey']
            aws s3 sync $srcpath $dirname --exclude "*" --include "$hnu*"
        }
        else 
        {
            write-output "no file $fnam found"
            set-location $loc
            Start-Sleep 10
        }
    }        
}
set-location $loc


