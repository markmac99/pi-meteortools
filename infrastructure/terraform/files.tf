# Copyright (C) Mark McIntyre
# upload the radio ini file


resource "aws_s3_object" "radioinifile" {
  key    = "radiostation.ini"
  bucket = "mjmm-rawradiodata"
  source = "files/radiostation.ini"
}
