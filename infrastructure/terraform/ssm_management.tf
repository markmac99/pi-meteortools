# SSM stuff for maintaining the webserver

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
