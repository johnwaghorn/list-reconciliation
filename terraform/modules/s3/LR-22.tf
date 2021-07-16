resource "aws_s3_bucket" "LR-22" {
  bucket        = "lr-22-pds-reg-output-${var.suffix}"
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "Output file storage for PDS practice extract files"
  }

  versioning {
    enabled = true
  }

  logging {
    target_bucket = aws_s3_bucket.LR-26.id
    target_prefix = "lr-22-pds-reg-output-${var.suffix}/"
  }
}
