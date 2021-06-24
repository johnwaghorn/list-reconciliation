data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../../lambdas/${var.lambda_name}"
  output_path = "${path.module}/../../../../lambdas/${var.lambda_name}.zip"
}

resource "aws_lambda_function" "LR-11-Lambda" {
  function_name = "${var.lambda_name}-${var.suffix}"
  filename = data.archive_file.lambda_zip.output_path
  handler = "gp_registration_status.lambda_handler"
  role = aws_iam_role.role.arn
  runtime = var.runtime
  timeout = var.lambda_timeout
  layers = [var.package_layer_arn]
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      DEMOGRAPHICS_TABLE = var.demographics_table_name
      JOBS_TABLE = var.jobs_table_name
      JOB_STATS_TABLE = var.job_stats_table_name
      ERRORS_TABLE = var.errors_table_name
      LR_13_REGISTRATIONS_OUTPUT_BUCKET = var.registrations_output_bucket
    }
  }
}
