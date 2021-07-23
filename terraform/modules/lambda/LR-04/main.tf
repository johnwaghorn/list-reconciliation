resource "aws_lambda_permission" "LR04_allow_LR01_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.LR-04-Lambda.arn
  principal     = "s3.amazonaws.com"
  source_arn    = var.source_bucket_arn
}
