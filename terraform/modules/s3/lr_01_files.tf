resource "aws_s3_bucket" "LR-01" {
  bucket        = "lr-01-gp-extract-input-${var.suffix}"
  acl           = "private"
  force_destroy = var.force_destroy

  tags = {
    Name = "S3 Input Bucket for LR-01 - ${var.suffix}"
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = var.kms_key_arn
        sse_algorithm     = "aws:kms"
      }
      bucket_key_enabled = true
    }
  }

  versioning {
    enabled = true
  }

  logging {
    target_bucket = aws_s3_bucket.LR-26.id
    target_prefix = "lr-01-gp-extract-input-${var.suffix}/"
  }
}
