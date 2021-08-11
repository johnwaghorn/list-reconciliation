resource "aws_config_config_rule" "api_gw_cache_enabled_and_encrypted" {
  name = "api-gw-cache-enabled-and-encrypted"

  source {
    owner             = "AWS"
    source_identifier = "API_GW_CACHE_ENABLED_AND_ENCRYPTED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "api_gw_execution_logging_enabled" {
  name             = "api-gw-execution-logging-enabled"
  input_parameters = jsonencode({ "loggingLevel" = "ERROR,INFO" })

  source {
    owner             = "AWS"
    source_identifier = "API_GW_EXECUTION_LOGGING_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}
