
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
