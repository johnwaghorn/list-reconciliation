resource "aws_lambda_permission" "allow_LR07_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = var.lr_06_bucket_arn
}

resource "aws_s3_bucket_notification" "bucket_notification_2" {
  bucket = var.lr_06_bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.lambda.arn
    events              = ["s3:ObjectCreated:*"]
  }
}
