resource "aws_s3_bucket" "LR-23" {
  bucket        = "lr-23-output-bucket-${var.suffix}"
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "File storage for data to be sent through MESH"
  }
}
