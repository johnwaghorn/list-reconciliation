#tfsec:ignore:custom-custom-lr-all-buckets-log tfsec:ignore:aws-s3-enable-versioning
resource "aws_s3_bucket" "LR-26" {
  bucket        = "lr-26-access-logs-${var.suffix}"
  acl           = "log-delivery-write"
  force_destroy = var.force_destroy

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle_rule {
    id      = "AccessLogs"
    enabled = true

    expiration {
      days = var.log_retention_in_days
    }
  }
}
