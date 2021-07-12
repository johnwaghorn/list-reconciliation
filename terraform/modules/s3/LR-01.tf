variable "s3_folders" {
  type        = list(string)
  description = "The list of S3 folders to create"
  default     = ["inbound", "fail", "pass", "retry"]
}

resource "aws_s3_bucket" "LR-01" {
  bucket        = "lr-01-gp-extract-input-${var.suffix}"
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "S3 Input Bucket for LR-01 - ${var.suffix}"
  }
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
