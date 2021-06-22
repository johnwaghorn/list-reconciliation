variable "s3_folders" {
  type        = list(string)
  description = "The list of S3 folders to create"
  default     = ["inbound", "fail", "pass", "ready"]
}

resource "aws_s3_bucket" "LR-01" {
  bucket        = lower("lr-01-${terraform.workspace}")
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "S3 Input Bucket for LR-01 - ${terraform.workspace}"
  }
}

resource "aws_s3_bucket" "LR-13" {
  bucket        = lower("lr-13-registration-differences-output-${terraform.workspace}")
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "Output file storage for LR-11 LR12 and LR14"
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
