resource "aws_s3_bucket" "LR-23" {
  bucket        = "lr-23-output-bucket-${var.suffix}"
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "File storage for data to be sent through MESH"
  }

  versioning {
    enabled = true
  }

  logging {
    target_bucket = aws_s3_bucket.LR-26.id
    target_prefix = "lr-23-output-bucket-${var.suffix}/"
  }
}
