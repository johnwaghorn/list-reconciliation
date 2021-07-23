resource "aws_lambda_permission" "LR02_allow_LR01_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.LR-02-Lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = var.source_bucket_arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.source_bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.LR-02-Lambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.lr_01_inbound_folder
  }

  lambda_function {
    lambda_function_arn = var.lr_04_lambda_arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.lr_01_failed_folder
    filter_suffix       = ".json"
  }
}