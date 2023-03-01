$curloc=get-location
set-location $PSScriptRoot
. .\helperfunctions.ps1
aws s3 cp s3://mjmm-rawradiodata/radiostation.ini .

$inifname = './radiostation.ini'
if ((test-path $inifname) -eq $false) {
    write-output "station.ini file missing or invalid, can't continue"
    exit 1
}

$ini=get-inicontent $inifname
$datadir=($ini['host']['datadir']).replace('/','\')
if((test-path $inifname) -eq $false){
    write-output "datadir missing or invalid, can't continue"
    exit 2
}
$arcdir=($ini['host']['archivedir'])
Set-Location $datadir
$txtdt=[string]$args[0]
#$jpgdt=$txtdt.substring(2)
$jpgdt=$txtdt

compress-archive -path sounds\event$txtdt*.wav -DestinationPath sounds\sound_$txtdt.zip
if ((test-path sounds\sound_$txtdt.zip) -eq 1)
{
    if ($arcdir.substring(0,5) -eq "s3://")
    {
        aws s3 mv sounds\sound_$jpgdt.zip $arcdir
    }
    else
    {
        Move-Item sounds\sound_$jpgdt.zip $arcdir -force
    }
    Remove-Item sounds\event$txtdt*.wav
}
compress-archive -path screenshots\event$jpgdt*.jpg -DestinationPath screenshots\images_$jpgdt.zip
if ((test-path screenshots\images_$jpgdt.zip) -eq 1)
{
    if ($arcdir.substring(0,5) -eq "s3://")
    {
        aws s3 mv screenshots\images_$jpgdt.zip $arcdir
    }
    else
    {
        Move-Item screenshots\images_$jpgdt.zip $arcdir -force
    }
    Remove-Item screenshots\event$jpgdt*.jpg
}
set-location $curloc
