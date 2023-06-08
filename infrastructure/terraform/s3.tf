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


resource "aws_s3_bucket_lifecycle_configuration" "mjmmdatalcp" {
  bucket = aws_s3_bucket.mjmm-data.id
  rule {
    status = "Enabled"
    id     = "purge old versions"
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
  rule {
    status = "Enabled"
    id     = "Transition to IA"
    #    filter {
    #      prefix = "archive/"
    #    }

    transition {
      days          = 45
      storage_class = "STANDARD_IA"
    }
  }
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name              = aws_s3_bucket.mjmm-data.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.mjmm-data-cfac.id
    origin_id                = aws_s3_bucket.mjmm-data.bucket_regional_domain_name 
  }
  enabled = true
  viewer_certificate {
    cloudfront_default_certificate = true
  }
  restrictions {
    geo_restriction {
      restriction_type = "none"
      locations        = []
    }
  }
  default_cache_behavior {
    # Using the CachingDisabled managed policy ID:
    cache_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"
    compress        = true
    allowed_methods = [
      "GET", 
      "HEAD"]
    target_origin_id       = aws_s3_bucket.mjmm-data.bucket_regional_domain_name 
    viewer_protocol_policy = "redirect-to-https"
    cached_methods         = ["GET", "HEAD"]
  }
  logging_config {
    bucket          = "mjmmauditing.s3.amazonaws.com"
    include_cookies = false
    prefix          = "mjmm-data-web"
  }
  ordered_cache_behavior {
    allowed_methods = [
      "GET",
      "HEAD",
    ]
    cache_policy_id = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    cached_methods = [
      "GET",
      "HEAD",
    ]
    compress               = true
    default_ttl            = 0
    max_ttl                = 0
    min_ttl                = 0
    path_pattern           = "/allsky/images/*.jpg"
    smooth_streaming       = false
    target_origin_id       = aws_s3_bucket.mjmm-data.bucket_regional_domain_name 
    trusted_key_groups     = []
    trusted_signers        = []
    viewer_protocol_policy = "allow-all"
  }
  ordered_cache_behavior {
    allowed_methods = [
      "GET",
      "HEAD",
    ]
    cache_policy_id = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    cached_methods = [
      "GET",
      "HEAD",
    ]
    compress               = true
    default_ttl            = 0
    max_ttl                = 0
    min_ttl                = 0
    path_pattern           = "/auroracam/*.jpg"
    smooth_streaming       = false
    target_origin_id       = aws_s3_bucket.mjmm-data.bucket_regional_domain_name 
    trusted_key_groups     = []
    trusted_signers        = []
    viewer_protocol_policy = "allow-all"
  }
  tags = {
    "billingtag" = "MarksWebsite"
  }
}

resource "aws_cloudfront_origin_access_control" "mjmm-data-cfac" {
  name = aws_s3_bucket.mjmm-data.bucket_regional_domain_name 
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

output "cfdistro_url" {
  value = aws_cloudfront_distribution.s3_distribution.domain_name
}

