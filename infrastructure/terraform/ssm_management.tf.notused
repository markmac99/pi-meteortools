# Copyright (C) Mark McIntyre
# SSM stuff for maintaining the webserver

# recover the Webserver details - this isn't currently managed by Terraform
data "aws_instance" "webserverid" {
  filter {
    name   = "dns-name"
    values = ["ec2-3-9-128-14.eu-west-2.compute.amazonaws.com"]
  }
}

# create a diskspace alarm
resource "aws_cloudwatch_metric_alarm" "webserverDiskspace" {
  alarm_name          = "webserverDiskspace"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  alarm_actions       = [aws_sns_topic.myalerts.arn, ]
  alarm_description   = "webserver diskspace exceeds 90pct"
  datapoints_to_alarm = 2
  dimensions = {
    ImageId      = data.aws_instance.webserverid.ami
    InstanceId   = data.aws_instance.webserverid.id
    InstanceType = data.aws_instance.webserverid.instance_type
    device       = "nvme0n1p1"
    fstype       = "ext4"
    path         = "/"
  }
  metric_name = "disk_used_percent"
  namespace   = "CWAgent"
  period      = 60
  statistic   = "Average"
  threshold   = 90
  tags = {
    billingtag = "MarksWebsite"
  }
}
# create an eventbridge rule to monitor the alarm
resource "aws_cloudwatch_event_rule" "webserverdiskspace" {
  name        = "webserver-diskspace"
  description = "Trigger when diskspace alarm goes off"

  event_pattern = <<EOF
{
  "detail-type": ["CloudWatch Alarm State Change"],
  "source": ["aws.cloudwatch"],
  "detail": {
    "alarmName": ["${aws_cloudwatch_metric_alarm.webserverDiskspace.alarm_name}"],
    "state": {
      "value": ["ALARM"]
    },
    "previousState": {
      "value": ["OK"]
    }
  }
}
EOF
  tags = {
    billingtag = "MarksWebsite"
  }
}

# target for the above rule
resource "aws_cloudwatch_event_target" "clearDiskspace" {
  arn      = aws_ssm_document.prunediskspace.arn
  rule     = aws_cloudwatch_event_rule.webserverdiskspace.name
  role_arn = aws_iam_role.ssmautomationrole.arn

  run_command_targets {
    key    = "InstanceIds"
    values = [data.aws_instance.webserverid.id]
  }
}

# create an SSM document to prune diskspace by running a script
resource "aws_ssm_document" "prunediskspace" {
  name            = "MJMM-PruneMySQLspace"
  document_format = "YAML"
  document_type   = "Command"
  tags = {
    billingtag = "MarksWebsite"
  }

  content = <<DOC
schemaVersion: '1.2'
description: Prune mysql indexes and compress tables
parameters: {}
runtimeConfig:
  'aws:runShellScript':
    properties:
      - id: '0.aws:runShellScript'
        runCommand:
          - /home/bitnami/src/maintenance/mysql_checks.sh
DOC
}

# IAM roles and policies used by the Run Command
data "aws_iam_policy_document" "ssm_lifecycle_trust" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "ssm_lifecycle" {
  statement {
    effect    = "Allow"
    actions   = ["ssm:SendCommand"]
    resources = [aws_ssm_document.prunediskspace.arn, data.aws_instance.webserverid.arn]
  }
}

resource "aws_iam_role" "ssmautomationrole" {
  name               = "AutomationServiceRole"
  path               = "/service-role/"
  assume_role_policy = data.aws_iam_policy_document.ssm_lifecycle_trust.json
  tags = {
    billingtag = "MarksWebsite"
  }
}

resource "aws_iam_policy" "automationservicepolicy" {
  name   = "AutomationServiceRole"
  policy = data.aws_iam_policy_document.ssm_lifecycle.json
  path   = "/service-role/"
  tags = {
    billingtag = "MarksWebsite"
  }
}

resource "aws_iam_role_policy_attachment" "ssm_lifecycle" {
  policy_arn = aws_iam_policy.automationservicepolicy.arn
  role       = aws_iam_role.ssmautomationrole.name
}

