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
  kms_key_id        = var.cloudwatch_kms_key.arn
}

resource "aws_lambda_function" "lambda" {
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
      DEMOGRAPHICS_TABLE      = var.demographics_table_name
      JOBS_TABLE              = var.jobs_table_name
      JOB_STATS_TABLE         = var.job_stats_table_name
      ERRORS_TABLE            = var.errors_table_name
      INFLIGHT_TABLE          = var.in_flight_table_name
      LR_10_STEP_FUNCTION_ARN = var.lr_10_step_function_arn
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}
