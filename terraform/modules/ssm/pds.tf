resource "aws_ssm_parameter" "pds_fhir_api_private_key" {
  name      = "/${var.prefix}/pds/pds_api_private_key"
  overwrite = true
  type      = "SecureString"
  value     = "To Replace"
  key_id    = var.ssm_kms_arn
}

resource "aws_ssm_parameter" "pds_fhir_access_token" {
  name      = "/${var.prefix}/pds/pds_api_access_token"
  overwrite = true
  type      = "SecureString"
  value     = "To Replace"
  key_id    = var.ssm_kms_arn
}

resource "aws_ssm_parameter" "pds_fhir_app_key" {
  name      = "/${var.prefix}/pds/pds_api_app_key"
  overwrite = true
  type      = "SecureString"
  value     = "To Replace"
  key_id    = var.ssm_kms_arn
}
