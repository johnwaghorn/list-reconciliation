resource "aws_config_config_rule" "cloudtrail_s3_dataevents_enabled" {
  name = "cloudtrail-s3-dataevents-enabled"

  source {
    owner             = "AWS"
    source_identifier = "CLOUDTRAIL_S3_DATAEVENTS_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "cloudtrail_encryption_enabled" {
  name = "cloudtrail-encryption-enabled"

  source {
    owner             = "AWS"
    source_identifier = "CLOUD_TRAIL_ENCRYPTION_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "cloudtrail_cloud_watch_logs_enabled" {
  name = "cloudtrail-cloud-watch-logs-enabled"

  source {
    owner             = "AWS"
    source_identifier = "CLOUD_TRAIL_CLOUD_WATCH_LOGS_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "cloudtrail_enabled" {
  name = "cloudtrail-enabled"

  source {
    owner             = "AWS"
    source_identifier = "CLOUD_TRAIL_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "cloudtrail_security_trail_enabled" {
  name = "cloudtrail-security-trail-enabled"

  source {
    owner             = "AWS"
    source_identifier = "CLOUDTRAIL_SECURITY_TRAIL_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "cloudtrail_log_file_validation_enabled" {
  name = "cloudtrail-log-file-validation-enabled"

  source {
    owner             = "AWS"
    source_identifier = "CLOUD_TRAIL_LOG_FILE_VALIDATION_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "cloudtrail_multi_region_enabled" {
  name = "cloudtrail-multi-region-enabled"

  source {
    owner             = "AWS"
    source_identifier = "MULTI_REGION_CLOUD_TRAIL_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}
