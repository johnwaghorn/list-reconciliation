locals {
  name           = "${var.lambda_name}-${var.suffix}"
  source_bucket  = var.source_bucket_arn
  lambda_timeout = 900
  memory_size    = 1024
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

resource "aws_lambda_function" "LR-02-Lambda" {
  function_name    = local.name
  filename         = data.archive_file.lambda_zip.output_path
  handler          = var.lambda_handler
  role             = aws_iam_role.role.arn
  runtime          = var.runtime
  memory_size      = local.memory_size
  timeout          = local.lambda_timeout
  layers           = var.lambda_layers
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      AWS_S3_REGISTRATION_EXTRACT_BUCKET = var.source_bucket
      JOBS_TABLE                         = var.jobs_table_name
      INFLIGHT_TABLE                     = var.in_flight_table_name
      LR_24_SAVE_RECORDS_TO_S3           = var.lr_24_lambda_arn
      LR_06_BUCKET                       = var.lr_06_bucket
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}