# Copyright (C) Mark McIntyre
# User, Policy and Roles used to mount s3 buckets. 
resource "aws_iam_user" "s3user" {
  name = "s3user"
  tags = {
    "billingtag" = "MarksWebsite"
  }
}

resource "aws_iam_policy" "MMS3BucketAccessRW" {
  name        = "MMS3BucketAccessRW"
  policy      = data.aws_iam_policy_document.MMS3BucketAccessRW-policy-doc.json
  description = "Access to MM S3 Buckets"
  tags = {
    "billingtag" = "MarksWebsite"
  }
}

data "aws_iam_policy_document" "MMS3BucketAccessRW-policy-doc" {
  statement {
    actions = ["s3:ListBucket"]
    effect  = "Allow"
    resources = [
      "arn:aws:s3:::${var.mlmwebsitebackupbucket}",
      "arn:aws:s3:::${var.websitebackupbucket}",
      "arn:aws:s3:::${var.meteoruploadbucket}",
      "arn:aws:s3:::${var.databucket}",
      "arn:aws:s3:::${var.satdatabucket}",
    ]
    sid = "VisualEditor0"
  }
  statement {
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:DeleteObject",
    ]
    effect = "Allow"
    resources = [
      "arn:aws:s3:::${var.mlmwebsitebackupbucket}/*",
      "arn:aws:s3:::${var.websitebackupbucket}/*",
      "arn:aws:s3:::${var.meteoruploadbucket}/*",
      "arn:aws:s3:::${var.databucket}/*",
      "arn:aws:s3:::${var.satdatabucket}/*",
    ]
    sid = "VisualEditor1"
  }
}

resource "aws_iam_user_policy_attachment" "s3user-pol-attachment" {
  user       = aws_iam_user.s3user.name
  policy_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/MMS3BucketAccessRW"
}

#inline policy used by s3user
resource "aws_iam_user_policy" "Ukmon-shared-access" {
  name = "Ukmon-shared-access"
  user = aws_iam_user.s3user.name
  policy = jsonencode(
    {
      Statement = [
        {
          Action = [
            "s3:GetObject",
            "s3:PutObject",
            "s3:PutObjectAcl",
          ]
          Effect = "Allow"
          Resource = [
            "arn:aws:s3:::${var.ukmonsharedbucket}/*",
            "arn:aws:s3:::${var.ukmonlivebucket}/*",
            "arn:aws:s3:::${var.ukmonwebbucket}/*",
          ]
        },
      ]
      Version = "2012-10-17"
    }
  )
}

# role for SSM hybrid device management
resource "aws_iam_role" "hybrid_ssm_role" {
  name        = "HybridSSMRole"
  description = "For managing on-prem infrastructure with SSM"
  assume_role_policy = jsonencode(
    {
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "ssm.amazonaws.com"
          },
        },
      ]
      Version = "2012-10-17"
    }
  )
  tags = {
    "billingtag" = "mmlocalhardware"
  }
}

resource "aws_iam_role_policy_attachment" "hybrid_ssm_role_att" {
  role       = aws_iam_role.hybrid_ssm_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

#activation of local SSM management
resource "aws_ssm_activation" "ssm_local_activation" {
  name               = "ssm_local_activation"
  description        = "Activation for on prem hardware"
  iam_role           = aws_iam_role.hybrid_ssm_role.id
  registration_limit = "20"
  depends_on         = [aws_iam_role_policy_attachment.hybrid_ssm_role_att]
  tags = {
    "billingtag" = "mmlocalhardware"
  }
}

output "activation_id" { value = aws_ssm_activation.ssm_local_activation.id }
output "activationcode" { value = aws_ssm_activation.ssm_local_activation.activation_code }
