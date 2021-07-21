resource "aws_s3_bucket" "LR-06" {
  bucket        = lower("lr-06-${var.suffix}")
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "S3 Bucket for LR-06 - ${var.suffix}"
  }
}
