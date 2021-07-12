locals {
  source_bucket  = "arn:aws:s3:::${var.supplementary-input-bucket}"
  lambda_timeout = 900
  memory_size    = 10240
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../../lambdas/${var.lambda_name}"
  output_path = "${path.module}/../../../../lambdas/${var.lambda_name}.zip"
}

resource "aws_lambda_function" "LR-21-Lambda" {
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
      LR_20_SUPPLEMENTARY_INPUT_BUCKET  = var.supplementary-input-bucket
      LR_22_SUPPLEMENTARY_OUTPUT_BUCKET = var.supplementary-output-bucket
      ERRORS_TABLE                      = var.errors_table_name
    }
  }
}