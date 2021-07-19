resource "aws_s3_bucket" "LR-23" {
  bucket        = "lr-23-output-bucket-${var.suffix}"
  acl           = "private"
  force_destroy = var.force_destroy

  tags = {
    Name = "File storage for data to be sent through MESH"
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = var.kms_key_arn
        sse_algorithm     = "aws:kms"
      }
    }
  }

  versioning {
    enabled = true
  }

  logging {
    target_bucket = aws_s3_bucket.LR-26.id
    target_prefix = "lr-23-output-bucket-${var.suffix}/"
  }
}

resource "aws_s3_bucket_public_access_block" "LR-23" {
  bucket = aws_s3_bucket.LR-23.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
