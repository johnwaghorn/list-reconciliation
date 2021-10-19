resource "aws_s3_bucket" "bucket" {
  bucket        = "${var.environment}-${var.name}"
  acl           = var.s3_acl
  force_destroy = var.s3_force_destroy_bucket

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = var.s3_kms_arn
        sse_algorithm     = "aws:kms"
      }
      bucket_key_enabled = true
    }
  }

  versioning {
    enabled = var.versioning_enabled
  }

  dynamic "logging" {
    for_each = var.s3_logging_enabled ? [var.name] : []

    content {
      target_bucket = var.s3_logging_bucket_name
      target_prefix = "${var.environment}-${var.name}/"
    }
  }
}
