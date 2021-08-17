resource "aws_ssm_parameter" "splunk_hec_endpoint_token" {
  name      = "/${var.prefix}/splunk/hec_endpoint_token"
  overwrite = true
  type      = "SecureString"
  value     = "00000000-0000-0000-0000-000000000000"
  key_id    = var.ssm_kms_arn

  lifecycle {
    ignore_changes = [
      value
    ]
  }
}
