resource "aws_cloudwatch_log_subscription_filter" "cloudwatch_to_firehose_filter" {
  name            = local.name
  role_arn        = var.cloudwatch_to_firehose_role_arn
  destination_arn = var.firehose_stream_arn
  log_group_name  = "/aws/lambda/${local.name}"
  filter_pattern  = ""
}
