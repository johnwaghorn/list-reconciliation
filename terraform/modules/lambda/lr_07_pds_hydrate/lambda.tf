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
  function_name                  = local.name
  filename                       = data.archive_file.lambda_zip.output_path
  handler                        = var.lambda_handler
  role                           = aws_iam_role.role.arn
  runtime                        = var.runtime
  timeout                        = 15 * 60 # 15 minutes
  layers                         = var.lambda_layers
  source_code_hash               = data.archive_file.lambda_zip.output_base64sha256
  reserved_concurrent_executions = var.lr_07_reserved_concurrent_executions

  environment {
    variables = {
      DEMOGRAPHICS_TABLE            = var.demographics_table_name
      DEMOGRAPHIC_COMPARISON_LAMBDA = var.lr_08_lambda
      PDS_BASE_URL                  = var.pds_base_url
      LR_06_BUCKET                  = var.lr_06_bucket
      SSM_STORE_PREFIX              = "/${var.pds_ssm_prefix}/"
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}
