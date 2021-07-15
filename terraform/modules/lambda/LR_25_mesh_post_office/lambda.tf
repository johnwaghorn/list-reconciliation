data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../../lambdas/${var.lambda_name}"
  output_path = "${path.module}/../../../../lambdas/${var.lambda_name}.zip"
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.name}"
  retention_in_days = 365
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
}
