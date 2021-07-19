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
}

resource "aws_s3_bucket_public_access_block" "LR-26" {
  bucket = aws_s3_bucket.LR-26.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
