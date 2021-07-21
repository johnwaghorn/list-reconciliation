resource "aws_s3_bucket" "LR-06" {
  bucket        = "lr-06-${var.suffix}"
  acl           = "private"
  force_destroy = var.force_destroy

  tags = {
    Name = "S3 Bucket for LR-06 - ${var.suffix}"
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

  logging {
    target_bucket = aws_s3_bucket.LR-26.id
    target_prefix = "lr-06-${var.suffix}/"
  }
}

resource "aws_s3_bucket_public_access_block" "lr_06" {
  bucket = aws_s3_bucket.LR-06.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
