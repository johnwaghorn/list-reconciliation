output "pds_api_mock" {
  value = aws_api_gateway_deployment.pds_api_mock_deployment
}

output "security_group" {
  value = aws_security_group.pds_api_mock
}
