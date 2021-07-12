resource "aws_lambda_permission" "allows_sqs_to_trigger_lambda" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.LR-07-Lambda.arn
  principal     = "sqs.amazonaws.com"
  source_arn    = var.patient_sqs_arn
}

resource "aws_lambda_event_source_mapping" "event_source" {
  batch_size       = 1
  event_source_arn = var.patient_sqs_arn
  enabled          = true
  function_name    = aws_lambda_function.LR-07-Lambda.arn
}
