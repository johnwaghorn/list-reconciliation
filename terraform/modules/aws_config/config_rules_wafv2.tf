resource "aws_config_config_rule" "wafv2_logging_enabled" {
  name = "wafv2-logging-enabled"

  source {
    owner             = "AWS"
    source_identifier = "WAFV2_LOGGING_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}
