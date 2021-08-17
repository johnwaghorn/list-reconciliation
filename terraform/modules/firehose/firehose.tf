resource "aws_kinesis_firehose_delivery_stream" "firehose_to_splunk_stream" {
  name        = local.name
  destination = "splunk"

  s3_configuration {
    role_arn           = aws_iam_role.role.arn
    bucket_arn         = var.firehose_failure_bucket_arn
    buffer_size        = 5
    buffer_interval    = 300
    compression_format = "GZIP"
  }

  splunk_configuration {
    hec_endpoint               = var.splunk_hec_endpoint
    hec_token                  = var.splunk_ssm_hec_token
    hec_acknowledgment_timeout = 300
    hec_endpoint_type          = "Event"
    s3_backup_mode             = "FailedEventsOnly"

    processing_configuration {
      enabled = "true"

      processors {
        type = "Lambda"

        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = "${var.transform_lambda_arn}:$LATEST"
        }

        parameters {
          parameter_name  = "RoleArn"
          parameter_value = aws_iam_role.role.arn
        }
      }
    }

    cloudwatch_logging_options {
      enabled        = true
      log_group_name = aws_cloudwatch_log_group.log_group.name
    }
  }
}

resource "aws_cloudwatch_log_group" "log_group" {
  name              = "/aws/firehose/${local.name}"
  retention_in_days = var.log_retention_in_days
  kms_key_id        = var.cloudwatch_kms_key.arn
}
