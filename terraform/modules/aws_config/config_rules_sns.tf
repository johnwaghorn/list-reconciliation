resource "aws_config_config_rule" "sns_encrypted_kms" {
  name = "sns-encrypted-kms"

  source {
    owner             = "AWS"
    source_identifier = "SNS_ENCRYPTED_KMS"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}
