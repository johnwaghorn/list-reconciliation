resource "aws_lambda_function" "lambda" {
  function_name                  = "${var.environment}-${var.name}"
  filename                       = data.archive_file.lambda_zip.output_path
  handler                        = var.handler
  role                           = aws_iam_role.role.arn
  runtime                        = var.runtime
  timeout                        = var.timeout
  layers                         = var.lambda_layers
  source_code_hash               = data.archive_file.lambda_zip.output_base64sha256
  reserved_concurrent_executions = var.reserved_concurrent_executions

  dynamic "environment" {
    for_each = length(var.environment_variables) > 0 ? ["Env"] : []

    content {
      variables = var.environment_variables
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}
