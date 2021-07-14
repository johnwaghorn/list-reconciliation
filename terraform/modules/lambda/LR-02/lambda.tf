locals {
  source_bucket  = "arn:aws:s3:::${var.source_bucket}"
  lambda_timeout = 900
  memory_size    = 1024
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../../lambdas/${var.lambda_name}"
  output_path = "${path.module}/../../../../lambdas/${var.lambda_name}.zip"
}

resource "aws_lambda_function" "LR-02-Lambda" {
  function_name    = "${var.lambda_name}-${var.suffix}"
  filename         = data.archive_file.lambda_zip.output_path
  handler          = var.lambda_handler
  role             = aws_iam_role.role.arn
  runtime          = var.runtime
  timeout          = local.lambda_timeout
  memory_size      = local.memory_size
  layers           = [var.package_layer_arn]
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256


  environment {
    variables = {
      AWS_PATIENT_RECORD_SQS             = var.patient_sqs_name
      AWS_S3_REGISTRATION_EXTRACT_BUCKET = var.source_bucket
      DEMOGRAPHICS_TABLE                 = var.demographics_table_name
      JOBS_TABLE                         = var.jobs_table_name
      INFLIGHT_TABLE                     = var.in_flight_table_name
      ERRORS_TABLE                       = var.errors_table_name
    }
  }
}
