# script to deploy the Windows scripts locally on my PC
set-location $PSScriptRoot
# load the helper functions
. .\DailyChecks\helperfunctions.ps1
# read the inifile
$ini=get-inicontent 'windows\UK0006.ini'
$targ=$ini['camera']['localfolder']+'\..\scripts\'
$targ=$targ.replace('/','\')

xcopy /dy /exclude:exclude.rsp .\Windows\*.ps1 $targ
xcopy /dy /exclude:exclude.rsp .\Windows\*.ini $targ

xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\NewAnalysis\*.py $targ
xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\NewAnalysis\*.ps1 $targ
xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\NewAnalysis\FormatConverters\*.py $targ
xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\NewAnalysis\orbitSolver\*.py $targ
xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\NewAnalysis\orbitSolver\*.ps1 $targ

if ((test-path $targ\CameraCurator) -eq 0 ){ mkdir $targ\CameraCurator }
xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\NewAnalysis\CameraCurator\*.py $targ\CameraCurator

if ((test-path $targ\UFOHandler) -eq 0 ){ mkdir $targ\UFOHandler }
xcopy /dy /exclude:exclude.rsp ..\ukmon-shared\NewAnalysis\UFOHandler\*.py $targ\UFOHandler

xcopy /dy .\Pi\sunwait-src\sunwait.exe $targ
xcopy /dy ..\ukmon-shared\UKMonCPPTools\stacker\build\Release\stacker.exe $targ
