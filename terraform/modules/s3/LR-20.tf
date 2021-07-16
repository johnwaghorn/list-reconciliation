resource "aws_s3_bucket" "LR-20" {
  bucket        = "lr-20-pds-reg-input-${var.suffix}"
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "Input file storage for PDS practice supplementary data"
  }

  versioning {
    enabled = true
  }

  logging {
    target_bucket = aws_s3_bucket.LR-26.id
    target_prefix = "lr-20-pds-reg-input-${var.suffix}/"
  }
}
