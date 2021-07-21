resource "aws_s3_bucket" "LR-22" {
  bucket        = "lr-22-pds-reg-output-${var.suffix}"
  acl           = "private"
  force_destroy = var.force_destroy

  tags = {
    Name = "Output file storage for PDS practice extract files"
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
    target_prefix = "lr-22-pds-reg-output-${var.suffix}/"
  }
}

resource "aws_s3_bucket_public_access_block" "LR-22" {
  bucket = aws_s3_bucket.LR-22.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
