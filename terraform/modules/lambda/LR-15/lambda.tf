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

resource "aws_lambda_function" "LR-15-Lambda" {
  function_name    = local.name
  filename         = data.archive_file.lambda_zip.output_path
  handler          = var.lambda_handler
  role             = aws_iam_role.role.arn
  runtime          = var.runtime
  timeout          = local.lambda_timeout
  layers           = [var.package_layer_arn]
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      DEMOGRAPHICS_TABLE                = var.demographics_table_name
      JOBS_TABLE                        = var.jobs_table_name
      JOB_STATS_TABLE                   = var.job_stats_table_name
      DEMOGRAPHICS_DIFFERENCES_TABLE    = var.demographics_differences_table_name
      MESH_BUCKET                       = var.mesh_send_bucket
      LR_13_REGISTRATIONS_OUTPUT_BUCKET = var.registrations_output_bucket
      MESH_SSM_PREFIX                   = "/${var.mesh_ssm}/"
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}
