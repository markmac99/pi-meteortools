# 
# script to backup or restore Pi configuration
#
# Copyright (C) Mark McIntyre

Push-Location $PSScriptRoot

if ($args[0] -eq "backup") 
{
	$targ=$args[1]
	bash -c "./backup-config.sh $targ"
}
elseif ($args[0] -eq "restore") 
{
	$targ=$args[1]
	bash -c "./restore-config.sh $targ"
}
else
{
	write-output "usage: configBkpRestore backup|restore pi_name"
}
Pop-Location