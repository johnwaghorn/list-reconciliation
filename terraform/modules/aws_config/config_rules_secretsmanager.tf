resource "aws_config_config_rule" "secretsmanager_rotation_enabled_check" {
  name = "secretsmanager-rotation-enabled-check"

  source {
    owner             = "AWS"
    source_identifier = "SECRETSMANAGER_ROTATION_ENABLED_CHECK"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "secretsmanager_scheduled_rotation_success_check" {
  name = "secretsmanager-scheduled-rotation-success-check"

  source {
    owner             = "AWS"
    source_identifier = "SECRETSMANAGER_SCHEDULED_ROTATION_SUCCESS_CHECK"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}
