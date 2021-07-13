resource "aws_s3_bucket" "LR-26" {
  bucket        = "lr-26-access-logs-${var.suffix}"
  acl           = "log-delivery-write"
  force_destroy = var.force_destroy
}

resource "aws_s3_bucket_public_access_block" "LR-26" {
  bucket = aws_s3_bucket.LR-23.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
