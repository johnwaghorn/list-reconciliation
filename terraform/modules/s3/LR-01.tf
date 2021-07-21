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

resource "aws_s3_bucket_public_access_block" "LR-01" {
  bucket = aws_s3_bucket.LR-01.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_object" "inbound" {
  bucket        = aws_s3_bucket.LR-01.id
  key           = "inbound/"
  acl           = "private"
  force_destroy = true
  content_type  = "application/x-directory"
}

resource "aws_s3_bucket_object" "pass" {
  bucket        = aws_s3_bucket.LR-01.id
  key           = "pass/"
  acl           = "private"
  force_destroy = true
  content_type  = "application/x-directory"
}

resource "aws_s3_bucket_object" "fail" {
  bucket        = aws_s3_bucket.LR-01.id
  key           = "fail/"
  acl           = "private"
  force_destroy = true
  content_type  = "application/x-directory"
}

resource "aws_s3_bucket_object" "retry" {
  bucket        = aws_s3_bucket.LR-01.id
  key           = "retry/"
  acl           = "private"
  force_destroy = true
  content_type  = "application/x-directory"
}
