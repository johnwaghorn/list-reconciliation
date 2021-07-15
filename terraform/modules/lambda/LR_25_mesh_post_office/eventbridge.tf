resource "aws_cloudwatch_event_rule" "schedule" {
  name                = local.name
  description         = local.name
  schedule_expression = var.event_schedule_expression
}

resource "aws_cloudwatch_event_target" "schedule" {
  rule      = aws_cloudwatch_event_rule.schedule.name
  target_id = "PostOfficeCheck"
  arn       = aws_lambda_function.lambda.arn
}
