resource "aws_lambda_permission" "allow_LR20_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.LR-21-Lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.supplementary-input-bucket}"
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.supplementary-input-bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.LR-21-Lambda.arn
    events              = ["s3:ObjectCreated:*"]
  }
}