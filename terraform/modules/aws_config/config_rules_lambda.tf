resource "aws_config_config_rule" "lambda_concurrency_check" {
  name = "lambda-concurrency-check"

  source {
    owner             = "AWS"
    source_identifier = "LAMBDA_CONCURRENCY_CHECK"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "lambda_function_public_access_prohibited" {
  name = "lambda-function-public-access-prohibited"

  source {
    owner             = "AWS"
    source_identifier = "LAMBDA_FUNCTION_PUBLIC_ACCESS_PROHIBITED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}
