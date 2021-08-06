
output "pds_ssm_parameters_path" {
  value = "${var.prefix}/pds"
}

output "pds_ssm_access_token" {
  value = aws_ssm_parameter.pds_fhir_access_token.arn
}

output "pds_ssm_private_key" {
  value = aws_ssm_parameter.pds_fhir_api_private_key.arn
}

output "pds_ssm_app_key" {
  value = aws_ssm_parameter.pds_fhir_app_key.arn
}
