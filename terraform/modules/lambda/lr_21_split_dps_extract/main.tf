resource "aws_lambda_permission" "allow_LR20_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.LR-21-Lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = var.supplementary_input_bucket_arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.supplementary_input_bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.LR-21-Lambda.arn
    events              = ["s3:ObjectCreated:*"]
  }
}
