# set the cloudwatch alarm tags

. ~/.ssh/mark-creds.ps1

aws cloudwatch tag-resource --resource-arn "arn:aws:cloudwatch:eu-west-2:317976261112:alarm:CalcServer diskspace" --tags Key=billingtag,Value=ukmon --region eu-west-2
aws cloudwatch tag-resource --resource-arn "arn:aws:cloudwatch:eu-west-2:317976261112:alarm:ukmonHelperDiskspace" --tags Key=billingtag,Value=ukmon --region eu-west-2
aws cloudwatch tag-resource --resource-arn "arn:aws:cloudwatch:eu-west-2:317976261112:alarm:awsec2-i-0da38ed8aea1a1d85-LessThanOrEqualToThreshold-CPUUtilization" --tags Key=billingtag,Value=ukmon --region eu-west-2
aws cloudwatch tag-resource --resource-arn "arn:aws:cloudwatch:eu-west-2:317976261112:alarm:Wordpress Diskspace Alert" --tags Key=billingtag,Value=MarysWebsite --region eu-west-2

aws cloudformation update-stack --stack-name createCamIndexes --use-previous-template --capabilities CAPABILITY_IAM --tags Key=billingtag,Value=MarksWebsite --region eu-west-2
aws cloudformation update-stack --stack-name processRadioData --use-previous-template --capabilities CAPABILITY_IAM --tags Key=billingtag,Value=MarksWebsite --region eu-west-2
aws cloudformation update-stack --stack-name processRadioJpgs --use-previous-template --capabilities CAPABILITY_IAM --tags Key=billingtag,Value=MarksWebsite --region eu-west-2