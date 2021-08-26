resource "aws_ssm_parameter" "parameter" {
  count = var.ignore_value_changes ? 0 : 1

  name      = "/${var.environment}/${var.name}"
  type      = var.type
  value     = var.value
  overwrite = true
  key_id    = var.ssm_kms_arn
}

resource "aws_ssm_parameter" "ignore_value_changes" {
  count = var.ignore_value_changes ? 1 : 0

  name      = "/${var.environment}/${var.name}"
  type      = var.type
  value     = var.value
  overwrite = true
  key_id    = var.ssm_kms_arn

  lifecycle {
    ignore_changes = [
      value
    ]
  }
}
