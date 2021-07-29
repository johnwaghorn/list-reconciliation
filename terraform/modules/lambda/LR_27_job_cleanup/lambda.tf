data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../../lambdas/${var.lambda_name}"
  output_path = "${path.module}/../../../../lambdas/${var.lambda_name}.zip"
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.name}"
  retention_in_days = var.log_retention_in_days
}

resource "aws_lambda_function" "lambda" {
  function_name    = local.name
  filename         = data.archive_file.lambda_zip.output_path
  handler          = "main.lambda_handler"
  role             = aws_iam_role.role.arn
  runtime          = var.runtime
  timeout          = 15 * 60 # 15 minutes
  layers           = [var.package_layer_arn]
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      LR_13_REGISTRATIONS_OUTPUT_BUCKET = var.lr_13_registrations_output_bucket
      JOBS_TABLE                        = var.jobs_table_name
      INFLIGHT_TABLE                    = var.in_flight_table_name
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}
