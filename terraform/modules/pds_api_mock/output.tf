output "pds_api_mock_deploy_url" {
  value = aws_api_gateway_deployment.pds_api_mock_deployment.invoke_url
}

output "pds_api_mock_arn" {
  value = aws_api_gateway_deployment.pds_api_mock_deployment.execution_arn
}
