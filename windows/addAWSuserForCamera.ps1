# Copyright (C) Mark McIntyre
if ($args.count -lt 1)
{
    Write-Output "usage: createUserKeyAWS.ps1 devicename"
    write-output "eg .\createUserKeyAWS.ps1 wxsatpi"
    exit
}
$username = $args[0]
$acct='317976261112'
$policyname = 's3AccessforAuroraCam'

if ((test-path "$psscriptroot\jsonkeys") -eq 0 ){
	mkdir "$psscriptroot\jsonkeys"
	mkdir "$psscriptroot\userdets"
	mkdir "$psscriptroot\creds"
}
$userdets = "$psscriptroot\userdets\$username.txt"
$keyf = "$psscriptroot\jsonkeys\$username.json"
$policyarn = 'arn:aws:iam::' + $acct + ':policy/' + $policyname

write-output "user $username being created if needed"
$res=(aws iam get-user --user-name $username --profile default) 
if (! $res) {
    aws iam create-user --user-name $username --profile default | out-file -filepath $userdets
}
write-output "creating key and saving it"
aws iam create-access-key --user-name $username --profile default | out-file -filepath $keyf
write-output "attaching policy and group"
aws iam attach-user-policy --policy-arn $policyarn --user-name $username  --profile default

write-output "converting key to credentials file"
$JSON = Get-Content $keyf | Out-String | ConvertFrom-Json
$keyid = $json.AccessKey.AccessKeyId
$secid = $json.AccessKey.SecretAccessKey
$csvf = "$PSscriptroot\creds\credentials." +$username
write-output "[default]" | out-file -filepath $csvf 
write-output "aws_access_key_id = $keyid" | out-file -filepath $csvf -Append
write-output "aws_secret_access_key = $secid" | out-file -filepath $csvf -Append
get-content $csvf