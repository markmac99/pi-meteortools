# powershell script to check radio meteor log and restart if it 
# seems to have stopped working
set-location $PSScriptRoot
. .\helperfunctions.ps1
$inifname = './station.ini'
if ((test-path $inifname) -eq $false) {
    write-output "station.ini file missing or invalid, can't continue"
    exit 1
}

$ini=get-inicontent $inifname
$datadir=($ini['detector']['datadir']).replace('/','\')
if((test-path $inifname) -eq $false){
    write-output "datadir missing or invalid, can't continue"
    exit 2
}

$offset=-0.5
$offsmin=-60*$offset
set-location $datadir

$logf=$datadir+'\logs\check-'+$dt+'.log'
write-output "Starting..." | tee-object $logf -append
while($true)
{
    $dt =get-date -uformat '%Y%m%d'
    $logf=$datadir+'\logs\check-'+$dt+'.log'
    $ftocheck=$datadir+'\event_log'+$dt+'.txt'

    if ((get-item $ftocheck).lastwritetime -lt  (get-date).addhours($offset)) 
    { 
        # need to handle midnight when the new file may not exist yet
        $hrmin=(get-date -uformat %H%M)
        $msg='checking at '+$hrmin
        write-output $msg |tee-object $logf -append
        if ([int]$hrmin -gt $offsmin)
        {
            $msg='radio meteor seems to have stopped at ' + $hrmin
            write-output $msg |tee-object $logf -append
            Send-MailMessage -from radiometeor@rm -to mark@localhost -subject "Radio down" -body $msg -smtpserver 192.168.1.151    
            $id=(Get-Process SDRSharp).id
            stop-process $id
            start-sleep(10)
            & scripts\runSDRSharp.exe
        }
    } 
    write-output 'Waiting 10 minutes...'
    Start-Sleep -seconds 600
}