resource "aws_ssm_parameter" "list_rec_email_password" {
  name   = "/${var.prefix}/email/list_rec_email_password"
  type   = "SecureString"
  value  = "To Replace"
  key_id = var.ssm_kms_arn

  lifecycle {
    ignore_changes = [
      value
    ]
  }
}
