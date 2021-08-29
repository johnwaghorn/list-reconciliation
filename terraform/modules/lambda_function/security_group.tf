resource "aws_security_group" "lambda" {
  name        = "${var.environment}-${var.name}"
  description = "${var.environment}-${var.name}"
  vpc_id      = var.vpc_id
}

resource "aws_security_group_rule" "egress_security_groups" {
  count = var.security_group_egresses_length

  description              = "Allow egress to Security Groups"
  security_group_id        = aws_security_group.lambda.id
  type                     = "egress"
  from_port                = var.security_group_egresses[count.index].port
  to_port                  = var.security_group_egresses[count.index].port
  protocol                 = "tcp"
  source_security_group_id = var.security_group_egresses[count.index].id
}

resource "aws_security_group_rule" "ingress_source_security_groups" {
  count = var.security_group_egresses_length

  description              = "Allow ingress from Security Groups"
  security_group_id        = var.security_group_egresses[count.index].id
  type                     = "ingress"
  from_port                = var.security_group_egresses[count.index].port
  to_port                  = var.security_group_egresses[count.index].port
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.lambda.id
}

resource "aws_security_group_rule" "egress_cidr_blocks" {
  count = var.cidr_block_egresses_length

  description       = "Allow egress to CIDR Blocks"
  security_group_id = aws_security_group.lambda.id
  type              = "egress"
  from_port         = var.cidr_block_egresses[count.index].port
  to_port           = var.cidr_block_egresses[count.index].port
  protocol          = "tcp"
  cidr_blocks       = [var.cidr_block_egresses[count.index].cidr_block]
}

resource "aws_security_group_rule" "egress_prefix_lists" {
  count = var.prefix_list_egresses_length

  description       = "Allow egress to Prefix Lists"
  security_group_id = aws_security_group.lambda.id
  type              = "egress"
  from_port         = var.prefix_list_egresses[count.index].port
  to_port           = var.prefix_list_egresses[count.index].port
  protocol          = "tcp"
  prefix_list_ids   = [var.prefix_list_egresses[count.index].id]
}
