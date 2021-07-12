resource "aws_lambda_permission" "allow_LR01_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.LR-02-Lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.source_bucket}"
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.source_bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.LR-02-Lambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.lr_01_inbound_folder
  }
}