# Copyright (C) 2018-2023 Mark McIntyre

data "aws_route53_zone" "mjmmwebsite" {
  zone_id = "Z2RFZ6MC0ICDVH"
}

# domain name to be used by APIs 
resource "aws_api_gateway_domain_name" "apigwdomain" {
  certificate_arn          = aws_acm_certificate_validation.apicert.certificate_arn
  domain_name              = aws_acm_certificate.apicert.domain_name
}

# ACM certificates for API Gateway domain name
resource "aws_acm_certificate" "apicert" {
  domain_name       = "api.markmcintyreastro.co.uk"
  validation_method = "DNS"
  provider = aws.us-east-1-prov
  tags = {
    billingtag = "apis"
  }
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "apicert" {
  certificate_arn         = aws_acm_certificate.apicert.arn
  validation_record_fqdns = [for record in aws_route53_record.mjmmwebsite_api : record.fqdn]
  provider = aws.us-east-1-prov
}

#Route 53 record in the hosted zone to validate the Certificate
resource "aws_route53_record" "mjmmwebsite_api" {
  zone_id = data.aws_route53_zone.mjmmwebsite.zone_id
  for_each = {
    for dvo in aws_acm_certificate.apicert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 300
  type            = each.value.type
}


# DNS entry for the api domain
resource "aws_route53_record" "apidnsentry" {
  name    = aws_api_gateway_domain_name.apigwdomain.domain_name
  type    = "A"
  zone_id = data.aws_route53_zone.mjmmwebsite.id
  depends_on = [aws_api_gateway_domain_name.apigwdomain]
  
  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.apigwdomain.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.apigwdomain.cloudfront_zone_id
  }
}

data "aws_api_gateway_rest_api" "saveACapi" {
  name = "saveACapi"
}

resource "aws_api_gateway_base_path_mapping" "saveACapi" {
  api_id      = data.aws_api_gateway_rest_api.saveACapi.id
  stage_name  = "Prod"
  domain_name = aws_api_gateway_domain_name.apigwdomain.domain_name
  base_path = "saveacapi"
}



