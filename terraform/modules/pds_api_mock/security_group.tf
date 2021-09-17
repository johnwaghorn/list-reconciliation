resource "aws_security_group" "pds_api_mock" {
  name        = var.name
  description = var.name
  vpc_id      = var.vpc_id
}
