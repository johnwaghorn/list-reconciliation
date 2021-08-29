resource "aws_security_group" "endpoint" {
  count = var.endpoint_type == "Interface" ? 1 : 0

  name        = "${var.environment}-${var.endpoint}-endpoint"
  description = "${var.environment}-${var.endpoint}-endpoint"
  vpc_id      = var.vpc_id
}
