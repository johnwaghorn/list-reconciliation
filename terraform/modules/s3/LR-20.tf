resource "aws_s3_bucket" "LR-20" {
  bucket        = "lr-20-pds-reg-input-${var.suffix}"
  acl           = "private"
  force_destroy = var.force_destroy

  tags = {
    Name = "Input file storage for PDS practice supplementary data"
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
    target_prefix = "lr-20-pds-reg-input-${var.suffix}/"
  }
}

resource "aws_s3_bucket_public_access_block" "LR-20" {
  bucket = aws_s3_bucket.LR-20.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
