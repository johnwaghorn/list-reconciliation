locals {
  name = "${var.lambda_name}-${var.suffix}"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../../lambdas/${var.lambda_name}"
  output_path = "${path.module}/../../../../lambdas/${var.lambda_name}.zip"
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.name}"
  retention_in_days = var.log_retention_in_days
}

resource "aws_lambda_function" "LR-08-Lambda" {
  function_name    = local.name
  filename         = data.archive_file.lambda_zip.output_path
  handler          = var.lambda_handler
  role             = aws_iam_role.role.arn
  runtime          = var.runtime
  timeout          = var.lambda_timeout
  layers           = [var.package_layer_arn]
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      DEMOGRAPHICS_TABLE             = var.demographics_table_name
      ERRORS_TABLE                   = var.errors_table_name
      DEMOGRAPHICS_DIFFERENCES_TABLE = var.demographics_differences_table_name
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}
