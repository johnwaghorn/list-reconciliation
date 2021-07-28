locals {
  source_bucket  = var.supplementary_input_bucket_arn
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
      LR_20_SUPPLEMENTARY_INPUT_BUCKET  = var.supplementary_input_bucket
      LR_22_SUPPLEMENTARY_OUTPUT_BUCKET = var.supplementary_output_bucket
      ERRORS_TABLE                      = var.errors_table_name
    }
  }
}