resource "aws_vpc_endpoint" "endpoint" {
  auto_accept         = var.auto_accept
  policy              = var.policy
  private_dns_enabled = var.endpoint_type == "Interface" ? var.private_dns_enabled : null
  route_table_ids     = var.endpoint_type == "Gateway" ? var.vpc_route_table_ids : null
  security_group_ids  = var.endpoint_type == "Interface" ? [aws_security_group.endpoint[0].id] : null
  service_name        = "com.amazonaws.${data.aws_region.current.name}.${var.endpoint}"
  subnet_ids          = var.endpoint_type != "Gateway" ? var.vpc_subnet_ids : null
  vpc_endpoint_type   = var.endpoint_type
  vpc_id              = var.vpc_id
}
