data "aws_api_gateway_rest_api" "pds_api_mock" {
  count = local.environment == "prod" ? 0 : 1

  name = "pds-api-mock"
}
