resource "aws_config_config_rule" "cloudwatch_loggroup_retention_period_check" {
  name             = "cloudwatch-loggroup-retention-period-check"
  input_parameters = jsonencode({ "MinRetentionTime" = "14" })

  source {
    owner             = "AWS"
    source_identifier = "CW_LOGGROUP_RETENTION_PERIOD_CHECK"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "cloudwatch_log_group_encrypted" {
  name = "cloudwatch-log-group-encrypted"

  source {
    owner             = "AWS"
    source_identifier = "CLOUDWATCH_LOG_GROUP_ENCRYPTED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "cloudwatch_alarm_action_check" {
  name = "cloudwatch-alarm-action-check"
  input_parameters = jsonencode({
    "alarmActionRequired" = "true", "insufficientDataActionRequired" = "true", "okActionRequired" : "false"
  })

  source {
    owner             = "AWS"
    source_identifier = "CLOUDWATCH_ALARM_ACTION_CHECK"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}
