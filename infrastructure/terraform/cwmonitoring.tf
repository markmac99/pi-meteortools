#
# Terraform to manage SSM and CW alerts
# 
# Copyright (C) Mark McIntyre


resource "aws_iam_role" "CloudWatchAgentServerRole" {
  name        = "CloudWatchAgentServerRole"
  description = "Allows server to run CloudWatch agent"
  assume_role_policy = jsonencode(
    {
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "ec2.amazonaws.com"
          }
        },
      ]
      Version = "2012-10-17"
    }
  )
  tags = {
    "billingtag" = "management"
  }
}

resource "aws_iam_instance_profile" "cwagentserverprofile" {
  name = "CloudWatchAgentServerRole"
  role = aws_iam_role.CloudWatchAgentServerRole.name
}

resource "aws_iam_role_policy_attachment" "cwpolicy1" {
  role       = aws_iam_role.CloudWatchAgentServerRole.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy_attachment" "cwpolicy2" {
  role       = aws_iam_role.CloudWatchAgentServerRole.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role" "CloudWatchAgentAdminRole" {
  name        = "CloudWatchAgentAdminRole"
  description = "Allows write permissions to SSM store for CloudWatch agent"
  assume_role_policy = jsonencode(
    {
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "ec2.amazonaws.com"
          }
        },
      ]
      Version = "2012-10-17"
    }
  )
  tags = {
    "billingtag" = "management"
  }
}

resource "aws_iam_instance_profile" "cwagentadminprofile" {
  name = "CloudWatchAgentAdminRole"
  role = aws_iam_role.CloudWatchAgentAdminRole.name
}

resource "aws_iam_role_policy_attachment" "cwpolicy3" {
  role       = aws_iam_role.CloudWatchAgentAdminRole.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentAdminPolicy"
}

resource "aws_iam_role_policy_attachment" "cwpolicy4" {
  role       = aws_iam_role.CloudWatchAgentAdminRole.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
