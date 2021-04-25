# script to deploy the Windows scripts locally on my PC
set-location $PSScriptRoot
# load the helper functions
. .\Windows\helperfunctions.ps1
# read the inifile
$ini=get-inicontent 'windows\UK0006.ini'
$targ=$ini['camera']['localfolder']+'\..\scripts\'
$targ=$targ.replace('/','\')

xcopy /dy /exclude:exclude.rsp .\Windows\*.ps1 $targ
xcopy /dy /exclude:exclude.rsp .\Windows\*.ini $targ
xcopy /dy /exclude:exclude.rsp .\Windows\*.py $targ

xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\DailyChecks\*.ps1 $targ
xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\analysis\*.ps1 $targ
xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\analysis\orbitSolver\*.ps1 $targ

if ((test-path $targ\converters) -eq 0 ){ mkdir $targ\converters }
xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\ukmon_pylib\converters\*.py $targ\converters
xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\ukmon_pylib\traj\*.py $targ

if ((test-path $targ\CameraCurator) -eq 0 ){ mkdir $targ\CameraCurator }
xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\analysis\CameraCurator\*.py $targ\CameraCurator

if ((test-path $targ\UFOHandler) -eq 0 ){ mkdir $targ\UFOHandler }
xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\analysis\UFOHandler\*.py $targ\UFOHandler

#xcopy /dy .\Pi\sunwait-src\sunwait.exe $targ
xcopy /dy ..\ukmon-shared\UKMonCPPTools\stacker\build\Release\stacker.exe $targ
