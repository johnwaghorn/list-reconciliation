locals {
  source_bucket  = "arn:aws:s3:::${var.source_bucket}"
  lambda_timeout = 300
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../../lambdas/${var.lambda_name}"
  output_path = "${path.module}/../../../../lambdas/${var.lambda_name}.zip"
}

resource "aws_lambda_function" "LR-02-Lambda" {
  function_name     = "${var.lambda_name}-${terraform.workspace}"
  filename          = data.archive_file.lambda_zip.output_path
  handler           = "main.lambda_handler"
  role              = aws_iam_role.role.arn
  runtime           = var.runtime
  timeout           = local.lambda_timeout
  layers            = [ var.package_layer_arn]
  source_code_hash  = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      AWS_PATIENT_RECORD_SQS = var.patient_sqs_arn
      AWS_S3_REGISTRATION_EXTRACT_BUCKET = var.source_bucket
    }
  }
}
