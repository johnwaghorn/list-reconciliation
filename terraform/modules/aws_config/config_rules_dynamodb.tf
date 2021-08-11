resource "aws_config_config_rule" "dynamodb_table_encrypted_kms" {
  name = "dynamodb-table-encrypted-kms"

  source {
    owner             = "AWS"
    source_identifier = "DYNAMODB_TABLE_ENCRYPTED_KMS"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "dynamodb_table_encryption_enabled" {
  name = "dynamodb-table-encryption-enabled"

  source {
    owner             = "AWS"
    source_identifier = "DYNAMODB_TABLE_ENCRYPTION_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "dynamodb_throughput_limit_check" {
  name = "dynamodb-throughput-limit-check"

  source {
    owner             = "AWS"
    source_identifier = "DYNAMODB_THROUGHPUT_LIMIT_CHECK"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "dynamodb_autoscaling_enabled" {
  name = "dynamodb-autoscaling-enabled"

  source {
    owner             = "AWS"
    source_identifier = "DYNAMODB_AUTOSCALING_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}
