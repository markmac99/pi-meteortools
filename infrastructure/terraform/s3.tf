# Copyright (C) Mark McIntyre
resource "aws_s3_bucket" "mjmmauditing" {
  force_destroy = false
  bucket        = "mjmmauditing"
  tags = {
    "billingtag" = "Management"
  }
  object_lock_enabled = false
}

resource "aws_s3_bucket" "mjmm-data" {
  bucket = "mjmm-data"
  tags = {
    "billingtag" = "MarksWebsite"
  }
  object_lock_enabled = false
}

resource "aws_s3_bucket_logging" "ukmslogging" {
  bucket = aws_s3_bucket.mjmm-data.id

  target_bucket = aws_s3_bucket.mjmmauditing.id
  target_prefix = "data/"
}

data "aws_s3_bucket" "rawradiodata" {
  bucket = "mjmm-rawradiodata"
}

resource "aws_s3_bucket_logging" "rrdlogging" {
  bucket = data.aws_s3_bucket.rawradiodata.id

  target_bucket = aws_s3_bucket.mjmmauditing.id
  target_prefix = "rawradiodata/"
}

data "aws_s3_bucket" "rawsatdata" {
  bucket = "mjmm-rawsatdata"
}

resource "aws_s3_bucket_logging" "rsdlogging" {
  bucket = data.aws_s3_bucket.rawsatdata.id

  target_bucket = aws_s3_bucket.mjmmauditing.id
  target_prefix = "rawsatdata/"
}
