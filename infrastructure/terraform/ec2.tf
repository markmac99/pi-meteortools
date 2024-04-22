# ssh key - this is created  by the UKMON stuff
data "aws_key_pair" "marks_key2" {
  key_name           = "marks_key2"
  #include_public_key = True
  #filter {
  #  name   = "Name"
  #  values = ["marks_key2"]
  #}
}
