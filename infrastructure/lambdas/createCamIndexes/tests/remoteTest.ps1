# test 
$dtstr=$args[0]
(get-content tests\testEvent.json ) -replace "YYYYMM","${dtstr}" > tests/latestEvent.json
aws lambda invoke --profile default --function-name createCamIndexes --log-type Tail --cli-binary-format raw-in-base64-out --payload file://tests/latestEvent.json  --region eu-west-2 ./ftpdetect.log
