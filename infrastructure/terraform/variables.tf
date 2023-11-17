# Copyright (C) Mark McIntyre
variable "profile" {
    description = "AWS creds to use"
    default = "default"
}
variable "region" {
        default = "eu-west-2"
}

variable "access_key" {
    description = "Access Key"
    default = ""
}

variable "secret_key" {
    description = "Secret Key"
    default = ""
}

variable "databucket" { default = "mjmm-data" }
variable "meteoruploadbucket" { default = "mjmm-meteor-uploads" }
variable "websitebackupbucket" { default = "mjmm-website-backups" }
variable "mlmwebsitebackupbucket" { default = "mlm-website-backups" }
variable "satdatabucket" { default = "mjmm-rawsatdata" }

#data used by the code in several places
data "aws_caller_identity" "current" {}

