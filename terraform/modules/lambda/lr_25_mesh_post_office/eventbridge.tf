resource "aws_cloudwatch_event_rule" "schedule" {
  count = var.lr_25_event_schedule_expression == null ? 0 : 1

  name                = local.name
  description         = local.name
  schedule_expression = var.lr_25_event_schedule_expression
}

resource "aws_cloudwatch_event_target" "schedule" {
  count = var.lr_25_event_schedule_expression == null ? 0 : 1

  rule      = aws_cloudwatch_event_rule.schedule[0].name
  target_id = "LR25Check"
  arn       = aws_lambda_function.lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  count = var.lr_25_event_schedule_expression == null ? 0 : 1

  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.schedule[0].arn
}
