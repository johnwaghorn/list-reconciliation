variable "s3_folders" {
  type        = list(string)
  description = "The list of S3 folders to create"
  default     = ["inbound", "fail", "pass", "ready"]
}

resource "aws_s3_bucket" "LR-01" {
  bucket        = "lr-01-${var.suffix}"
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

resource "aws_s3_bucket" "LR-13" {
  bucket        = "lr-13-reg-diffs-output-${var.suffix}"
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "Output file storage for LR-11 LR-12 and LR-14"
  }
}

resource "aws_s3_bucket" "LR-22" {
  bucket        = "lr-22-pds-practice-registrations-${var.suffix}"
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "File storage for PDS practice extract files"
  }
}

resource "aws_s3_bucket" "mock-pds-data" {
  bucket        = "mock-pds-data-${var.suffix}"
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "File storage for PDS mock api data"
  }
}

resource "aws_s3_bucket" "LR-23" {
  bucket        = "lr-23-output-bucket-${var.suffix}"
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "File storage for data to be sent through MESH"
  }
}
