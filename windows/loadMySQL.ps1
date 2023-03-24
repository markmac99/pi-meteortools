# Copyright (C) Mark McIntyre
# powershell script to load UFOCAP csv files into MySQL
# database details all stored in the ini file 

$curloc=get-location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1

if ($args.count -eq 0) {
    $inifname='TACKLEY_TC.ini'
}
else {
    $inifname = $args[0]
}
$ini=get-inicontent $inifname
$camname=$ini['camera']['camera_name']
$localfolder=($ini['camera']['localfolder']).replace('/','\')
$username=$ini['mysql']['userid']
$password=(get-content $ini['mysql']['remotepass'])
$server=$ini['mysql']['server']
$database=$ini['mysql']['database']

$yy = get-date -format "yyyy"
$mm1 = get-date -format "MM"
$mm1=$mm1-1
$mm=([string]$mm1).padleft(2,'0')

$logf= -join("..\logs\loadmysql-$camname-", (get-date -uformat "%Y%m%d"),".log")

[void][reflection.assembly]::LoadFrom("e:\Documents\WindowsPowerShell\Modules\Renci.SshNet.dll")

if(!(get-command Connect-MySqlServer -errorAction SilentlyContinue)) { 
    import-module E:\Documents\WindowsPowerShell\Modules\mysql
}

$secureStringPwd = $password | ConvertTo-SecureString -AsPlainText -Force 
$dbcred = New-Object System.Management.Automation.PSCredential -ArgumentList $username, $secureStringPwd

Connect-MySqlServer  -Credential $dbcred -ComputerName $server -database $database

#Define our column headings (needed for the Insert statement)
$columns="Ver,Shower,csvLocalTime,Mag,Dur_sec,AV_deg_s,Loc_Cam,TZ,YY,MM,DD,HH,MI,SS,Dir1,"`
+ "Alt1,RA1,Dec1,RA2,Dec2,alpha,delta,x1,x2,x3,x4,x5,io,err1,err2,G1,dd1,dr1,"`
+" Vo,dV,ra_m,dec_m,refs,errm,rat,dct,voo,vooerr,tmerr,sps,sN,drop2"

$fn = get-childitem "*$yy$mm*$camname.csv" -recurse -name -path "$localfolder"
if ($fn)
{
    Write-Output "Uploading camera $camname for $yy $mm" > $logf
    $fn2 = "$localfolder\$fn"
    # clear the current month from the table
    $query="delete from ufocsvimport where yy=$yy and mm=$mm and loc_cam='$camname'"
    Invoke-MySqlQuery -Query $query -Verbose

    #import our csv
    $csv = import-csv $fn2 | Select-Object

    # iterate over the collection of data, constructing a sql string and executing an insert
    ForEach ($record in $csv){
        $query = "INSERT INTO ufocsvimport ($columns) VALUES ('$($record.ver)','$($record.group)',`
                '$($record.Localtime)',$($record.mag),$($record.'Dur(sec)'),`
                $($record.'AV(deg/s)'),'$($record.Loc_cam)',$($record.'TZ(h)'),$($record.'Y(UT)'),`
                $($record.'M(UT)'),$($record.'D(UT)'),$($record.'H(UT)'),$($record.M),`
                $($record.S),$($record.Dir1),$($record.Alt1),$($record.RA1),$($record.Dec1),`
                $($record.RA2),$($record.Dec2),$($record.alpha),$($record.delta ),$($record.H1),`
                $($record.H2),$($record.H3),$($record.H4),$($record.H5 ),$($record.io),`
                $($record.err1),$($record.err2),'$($record.G1)',$($record.'dd(deg)'),$($record.'dr(deg)'),`
                $($record.'Vo(km/s)'),$($record.'dV(%)'),$($record.ra_m),$($record.dec_m),`
                $($record.refs),$($record.errm),$($record.rat),$($record.dct),$($record.voo),`
                $($record.vooerr),$($record.tmerr),$($record.sps),$($record.sN),$($record.drop)`
                );"

                Write-Output "about to insert a value for :$($record.localtime)" >>$logf
        
        Invoke-MySqlQuery -Query $query
        start-sleep -Milliseconds 150
    }
    Invoke-MySqlQuery -Query "select count(shower) from ufocsvimport where YY=$yy and MM=$mm" >> $logf
}
else {
    Write-Output "File not found for camera $camname for $YY $MM" >> $logf
}
Disconnect-MySqlServer
set-location $curloc