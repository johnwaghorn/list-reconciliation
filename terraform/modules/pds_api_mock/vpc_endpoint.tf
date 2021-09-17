# https://medium.com/@ilia.lazebnik/simplifying-aws-private-api-gateway-vpc-endpoint-association-with-terraform-b379a247afbf

data "aws_security_group" "pds_api_mock" {
  vpc_id = var.vpc_id
  name   = "default"
}

data "aws_vpc_endpoint_service" "pds_api_mock" {
  service = "execute-api"
}

resource "aws_vpc_endpoint" "pds_api_mock" {
  vpc_id              = var.vpc_id
  service_name        = data.aws_vpc_endpoint_service.pds_api_mock.service_name
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true

  subnet_ids         = var.vpc_subnet_ids
  security_group_ids = [data.aws_security_group.pds_api_mock.id]
}
