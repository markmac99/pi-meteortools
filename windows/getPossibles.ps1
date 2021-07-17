# script to copy potential meteors that were missed by RMS
# this script grabs all the FF files for which there is a corresponding FR file.
# These are events that RMS thought there may have been bright enough, even
# if it was then unable to analyse it further. 
#
# The script copies the files from the Pi, converts them into JPGs then opens an explorer 
# window so you can manually inspect them
#
# Usage: getPossibles.ps1 {inifile} {datestamp}
# eg     getPossibles.ps1 UK0006.ini 20200811
#

set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -lt 2) {
    write-output "Usage: getPossibles.ps1 UK0006.ini datestampedfolder"
    exit 1
}
$inifname = $args[0]
if ((test-path $inifname) -eq $false) {
    write-output "ini file missing or invalid, can't continue"
    exit 1
}

$ini=get-inicontent $inifname
$hostname=$ini['camera']['hostname']
$localfolder=$ini['camera']['localfolder']
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']

conda activate $rms_env
$srcdir='\\'+$hostname+'\RMS_Data\CapturedFiles\*'+$args[1]+'*'
$srcdirs=(get-childitem $srcdir).fullname
$targdir=$localfolder+'/Interesting/'+$args[1]
$arcfil=$localfolder+'/ArchivedFiles/*'+$args[1]+'*/*.fits'

if ((test-path $targdir) -eq $false) { mkdir $targdir | out-null }

# if RMS restarts in the night you may have two folders for that night
for($i=0; $i -lt $srcdirs.count ; $i++)
{
    if($srcdirs.count -eq 1 ){$srcdir=$srcdirs} else { $srcdir=$srcdirs[$i]}
    
    Set-Location $srcdir
    $flist=(Get-ChildItem "*.bin").basename # all possible events
    $gotlist=(Get-ChildItem $arcfil).basename # list of events already captured

    write-output $srcdir
    if ($flist.length -gt 0) {
        for ($i=0;$i -lt $flist.length;$i++)
        {
            $fn="FF_"+$flist[$i].substring(3)
            if($gotlist -contains $fn){
                $msg='skipping '+$fn+'.fits'
                write-output $msg
            }else{
                $fn=$fn+".fits"
                write-output $fn  
                Copy-Item $fn $targdir
                $binf= $flist[$i]+'.bin'
                write-output $binf
                copy-item $binf $targdir
            }
        }
        Set-Location $rms_loc
        python -m Utils.BatchFFtoImage $targdir jpg
        $platepar=$localfolder+'/ArchivedFiles/*'+$args[1]+'*/platepar*'
        write-output "copying $platepar"
        copy-item $platepar $targdir
        Set-Location $PSScriptRoot
    #    explorer ($targdir).replace('/','\')
    }
    else {
        write-output "nothing of interest"
    }        
}
Set-Location $PSScriptRoot