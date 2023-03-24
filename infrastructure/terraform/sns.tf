# Copyright (C) Mark McIntyre
# SNS topics etc for alerting

resource "aws_sns_topic" "myalerts" {
  name = "emailAlertingTopic"
  tags = {
    billingtag="MarksWebsite"
  }
}

resource "aws_sns_topic_subscription" "snsemailsubs" {
  topic_arn = aws_sns_topic.myalerts.arn
  protocol  = "email"
  endpoint  = "markmcintyre99@googlemail.com"
}