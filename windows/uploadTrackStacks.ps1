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
$webserver=$ini['website']['webserver']


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
    $destpath=$localfolder+'\..\tmpstack\'
    
    $fnam = "$srcpath$hostname" + "_$ymd" + "*track_stack.jpg"
    
    $stackfile = (Get-ChildItem  $fnam ).Name
    
    if ($stackfile.length -ne 0)
    {
        $env:pythonpath=$pylib
        python -m utils.annotateImage $srcpath\$stackfile $hostname $metcount $ymd
        $newname=$hostname.toupper() + '_' + $ymd + '.jpg'
        Copy-Item $srcpath\$stackfile $destpath\$newname -force
    
        set-location "$destpath"
        $dirname = "data/mjmm-data/" + $hostname.toupper() + "/trackstacks"
        #ssh $webserver "mkdir $dirname > /dev/null 2>&1"
        $webtarg=$webserver+":"+$dirname
        scp $newname $webtarg
        remove-item $newname
    }
    else {
        Write-Output 'no stack to upload'
    }
        
}
set-location $loc


