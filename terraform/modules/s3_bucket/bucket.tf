resource "aws_s3_bucket" "bucket" {
  bucket        = "${var.environment}-${var.name}"
  acl           = var.name == "lr-26-access-logs" ? "log-delivery-write" : "private"
  force_destroy = var.s3_force_destroy_bucket

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = var.s3_logging_kms_arn
        sse_algorithm     = "aws:kms"
      }
      bucket_key_enabled = true
    }
  }

  versioning {
    enabled = var.versioning_enabled
  }

  dynamic "logging" {
    # we don't want to collect logs from the logging bucket itself
    for_each = var.name != "lr-26-access-logs" ? [var.name] : []

    content {
      target_bucket = var.s3_logging_bucket_name
      target_prefix = "${var.environment}-${var.name}/"
    }
  }
}
