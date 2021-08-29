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

  vpc_config {
    security_group_ids = [aws_security_group.lambda.id]
    subnet_ids         = var.vpc_subnet_ids
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda,
    aws_iam_role_policy_attachment.policy_vpc_attachment
  ]
}
