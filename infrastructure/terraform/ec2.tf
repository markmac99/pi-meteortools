# Copyright (C) Mark McIntyre
data "aws_security_group" "launch-wizard-4" {
  id = "sg-0b7fab84089059501"
}
/*
resource "aws_instance" "adminserver" {
  ami                  = "ami-03e88be9ecff64781"
  instance_type        = "t3a.nano"
  iam_instance_profile = aws_iam_instance_profile.cwagentadminprofile.name
  key_name             = data.aws_key_pair.marks_key2.key_name
  security_groups      = [data.aws_security_group.launch-wizard-4.name]
  tags = {
    "Name"       = "admin"
    "billingtag" = "Management"
  }
}
*/
# ssh key - this is created  by the UKMON stuff
data "aws_key_pair" "marks_key2" {
  key_name           = "marks_key2"
  #include_public_key = True
  #filter {
  #  name   = "Name"
  #  values = ["marks_key2"]
  #}
}
