# test the ML routine
# Copyright (C) Mark McIntyre

Write-Output "starting" > F:\videos\MeteorCam\logs\testml.log

$dirs = (Get-ChildItem F:\videos\MeteorCam\UK0006\ArchivedFiles\UK0006_202207*).fullname
foreach ($dir in $dirs) { python -m usertools.compareMLtoManual $dir >> F:\videos\MeteorCam\logs\testml.log } 

$dirs = (Get-ChildItem F:\videos\MeteorCam\UK000F\ArchivedFiles\UK000F_202207*).fullname
foreach ($dir in $dirs) { python -m usertools.compareMLtoManual $dir >> F:\videos\MeteorCam\logs\testml.log }

$dirs = (Get-ChildItem F:\videos\MeteorCam\UK001L\ArchivedFiles\UK001L_202207*).fullname
foreach ($dir in $dirs) { python -m usertools.compareMLtoManual $dir >> F:\videos\MeteorCam\logs\testml.log }

$dirs = (Get-ChildItem F:\videos\MeteorCam\UK002F\ArchivedFiles\UK002F_202207*).fullname
foreach ($dir in $dirs) { python -m usertools.compareMLtoManual $dir >> F:\videos\MeteorCam\logs\testml.log }