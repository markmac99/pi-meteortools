# 
# Uploads rejected/confirmed data to RMS for training the ML toolset
# 

set-location $PSScriptRoot

$srcpath = $args[0]
$spl = $srcpath.split('\')
$ns = $spl.count
$dirloc = $spl[$ns-1]
if ($dirloc -eq "" ) { $dirloc = $spl[$ns-2] }

$rp = $srcpath.replace('Archived','Rejected')
$tp = test-path $rp
$nf = (Get-ChildItem $rp).count
if (($nf -gt 0) -and ($tp -eq 1)) 
{
    Write-Output "in $rp"
    Push-Location $rp
    Write-Output "cd /files/RejectedFiles" > ../upload.txt
    Write-Output "mkdir $dirloc" >> ../upload.txt 
    Write-Output "cd $dirloc" >> ../upload.txt
    Write-Output "progress" >> ../upload.txt
    Write-Output "mput *" >> ../upload.txt
    write-output "bye" >> ../upload.txt
    # convert to unix format
    ((get-content ..\upload.txt) -join "`n") +"`n" | set-content -nonewline ..\upload.txt
    sftp -b ../upload.txt -i ~/.ssh/id_gmnrejected mldataset@gmn.uwo.ca 
    if ($? -eq 0)
    {
        Write-Output "trying without mkdir "
        Write-Output "cd /files/RejectedFiles" > ../upload.txt
        Write-Output "cd $dirloc" >> ../upload.txt
        Write-Output "progress" >> ../upload.txt
        Write-Output "mput *" >> ../upload.txt
        write-output "bye" >> ../upload.txt
        # convert to unix format
        ((get-content ..\upload.txt) -join "`n") +"`n" | set-content -nonewline ..\upload.txt
        sftp -b ../upload.txt -i ~/.ssh/id_gmnrejected mldataset@gmn.uwo.ca 
        Remove-Item ../upload.txt
    }
    Write-Output "done $rp"
    Pop-Location
}else {
    write-output "nothing to upload"
}

$rp = $srcpath.replace('Archived','Confirmed')

$tp = test-path $rp
$nf = (Get-ChildItem $rp).count
if (($nf -gt 0) -and ($tp -eq 1))
{
    Write-Output "in $rp"
    Push-Location $rp
    Write-Output "cd /files/ConfirmedFiles" > ../upload.txt
    Write-Output "mkdir $dirloc" >> ../upload.txt 
    Write-Output "cd $dirloc" >> ../upload.txt
    Write-Output "progress" >> ../upload.txt
    Write-Output "mput *" >> ../upload.txt
    write-output "bye" >> ../upload.txt
    # convert to unix format
    ((get-content ..\upload.txt) -join "`n") +"`n" | set-content -nonewline ..\upload.txt
    sftp -b ../upload.txt -i ~/.ssh/id_gmnrejected mldataset@gmn.uwo.ca 
    if ($? -eq 0)
    {
        Write-Output "trying without mkdir "
        Write-Output "cd /files/ConfirmedFiles" > ../upload.txt
        Write-Output "cd $dirloc" >> ../upload.txt
        Write-Output "progress" >> ../upload.txt
        Write-Output "mput *" >> ../upload.txt
        write-output "bye" >> ../upload.txt
        # convert to unix format
        ((get-content ..\upload.txt) -join "`n") +"`n" | set-content -nonewline ..\upload.txt
        sftp -b ../upload.txt -i ~/.ssh/id_gmnrejected mldataset@gmn.uwo.ca 
        Remove-Item ../upload.txt
    }
    Pop-Location
    Write-Output "done $rp"
}else {
    write-output "nothing to upload"
}


