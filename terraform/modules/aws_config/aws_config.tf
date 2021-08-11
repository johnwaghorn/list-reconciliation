resource "aws_config_configuration_recorder" "nhsd_config" {
  name     = local.name
  role_arn = aws_iam_role.config.arn
}

resource "aws_config_delivery_channel" "config_delivery_channel" {
  name           = local.name
  s3_bucket_name = "nhsd-audit-cloudtrail"
  s3_key_prefix  = "config"
  sns_topic_arn  = aws_sns_topic.config.arn

  snapshot_delivery_properties {
    delivery_frequency = "One_Hour"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_configuration_recorder_status" "recorder_status" {
  name       = aws_config_configuration_recorder.nhsd_config.name
  is_enabled = true

  depends_on = [aws_config_delivery_channel.config_delivery_channel]
}
