locals {
  lambda_timeout = 300
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../../lambdas/${var.lambda_name}"
  output_path = "${path.module}/../../../../lambdas/${var.lambda_name}.zip"
}

resource "aws_lambda_function" "Lambda" {
  function_name    = "${var.lambda_name}-${terraform.workspace}"
  filename         = data.archive_file.lambda_zip.output_path
  handler          = "pds_hydrate.lambda_handler"
  role             = aws_iam_role.role.arn
  runtime          = var.runtime
  timeout          = local.lambda_timeout
  layers           = [var.package_layer_arn]
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      DEMOGRAPHICS_TABLE            = var.demographics_table_name
      ERRORS_TABLE                  = var.errors_table_name
      DEMOGRAPHIC_COMPARISON_LAMBDA = var.lr_08_lambda
      PDS_API_URL                   = var.pds_url
    }
  }
}
