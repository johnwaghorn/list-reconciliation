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
  function_name    = local.name
  filename         = data.archive_file.lambda_zip.output_path
  handler          = var.lambda_handler
  role             = aws_iam_role.role.arn
  runtime          = var.runtime
  timeout          = 60 * 15   # 15 minutes
  memory_size      = 1024 * 10 # 10GB
  layers           = var.lambda_layers
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      LR_20_SUPPLEMENTARY_INPUT_BUCKET  = var.supplementary_input_bucket
      LR_22_SUPPLEMENTARY_OUTPUT_BUCKET = var.supplementary_output_bucket
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}

resource "aws_lambda_permission" "allow_LR20_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = var.supplementary_input_bucket_arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.supplementary_input_bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.lambda.arn
    events              = ["s3:ObjectCreated:*"]
  }
}
