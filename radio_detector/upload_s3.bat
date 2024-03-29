:: Batch file to upload a file to a web site via S3.
:: Uses the AWS CLI client (https://aws.amazon.com/cli/), typically invoked from SL's conditional actions.
::
:: Place this file in the Spectrum Lab directory.
::
:: You will need to create an AWS S3 bucket to store the uploaded files and configure it, e.g. meteorbucket. Read the documentation!
::   Create a folder within the bucket to hold the uploaded capture and log files, e.g. meteordata
::   Hint: You will need to configure the bucket policy to permit public read access if you want to serve the files over the web publically.
::   Hint: You may want to turn off or limit bucket versioning as the "interesting_n.jpg" files will generate lots of copies over time.
::   Hint: You will need to configure a CORS policy if you want to access S3 files via JavaScript from your web site.
::
:: You will need to install the S3 CLI and configure it on your SL PC to upload files to the bucket created above:
::   Download and install the S3 CLI using the Windows MSI installer from the link at the top.
::   Open a command prompt as administrator.
::   Type in the command prompt: aws configure
::   When prompted, you will need to enter the following (you should have obtained and saved the keys when creating the S3 bucket!):
::     AWS Access Key ID
::     AWS Secret Access Key
::     Default region name (where you created the bucket, e.g. eu-west-2 )
::     Default output format (set this to: json )
::
:: You will then need to modify the FTP settings in the SL Conditional Actions window:
::  Upload_Capture    (set to 1 to enable capture uploading )
::  Upload_Log        (set to 1 to enable log file uploading )
::  Upload_Threshold  (set to the miniumum SNR in dB to trigger a capture, e.g. 30 )
::  Upload_Limit      (the maximum number of upload files to retain before overwriting on a round-robin basis, e.g. 9 )
::  Upload_Method     (set to s3 )
::  Hostname_Bucket   (set to the bucket name created above, e.g. meteorbucket )
::  Upload_Directory  (set to a folder you have created within the s3 bucket, e.g. /meteordata/ include leading and trailing slashes)
::  S3_ACL            (set to public-read to make files accessible via http(s), or private to limit access to authorised S3 users)
::  IMPORTANT: If any of the values above contain a backslash (\) character, you must replace it with a double backslash (\\).
::
:: The upload filename will be generated by the conditional actions as: interesting_n.jpg where n is 1...Upload_Limit.
:: Usage: upload_s3.bat "upload path" "upload filename" "Hostname_Bucket" "Upload_Directory" "ignored" "ignored" "ignored" "ignored" "S3_ACL"
::                       %~1           %~2               %~3               %~4                %~5       %~6       %~7       %~8       %~9
:: Note the usage of %~1 not %1. The conditional actions add quotes around each parameter to deal with any spaces or special characters, %~1 strips them again.

:: Change to the upload path
cd %~1

:: Now call the AWS CLI to do the upload.
aws s3 cp %~1%~2 s3://%~3%~4 --acl %~9 
echo %date% %time% Command Executed: aws s3 cp %~1%~2 s3://%~3%~4 --acl %~9 > s3log.txt
:: Results from last run may be found in s3log.txt
:: Note the AWS CLI doesn't output errors to the console so add a temporary pause command below to review them interactively.
:End