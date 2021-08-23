locals {
  name           = "${var.lambda_name}-${var.suffix}"
  lambda_timeout = 300
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

resource "aws_lambda_function" "LR-12-Lambda" {
  function_name    = local.name
  filename         = data.archive_file.lambda_zip.output_path
  handler          = var.lambda_handler
  role             = aws_iam_role.role.arn
  runtime          = var.runtime
  timeout          = local.lambda_timeout
  layers           = var.lambda_layers
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      DEMOGRAPHICS_TABLE                      = var.demographics_table_name
      JOBS_TABLE                              = var.jobs_table_name
      JOB_STATS_TABLE                         = var.job_stats_table_name
      LR_13_REGISTRATIONS_OUTPUT_BUCKET       = var.registrations_output_bucket
      LR_22_PDS_PRACTICE_REGISTRATIONS_BUCKET = var.pds_practice_registrations_bucket
      PDS_BASE_URL                            = var.pds_base_url
      PDS_API_RETRIES                         = var.pds_api_retries
      SSM_STORE_PREFIX                        = "/${var.pds_ssm_prefix}/"
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}
