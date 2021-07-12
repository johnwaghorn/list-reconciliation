resource "aws_s3_bucket" "LR-20" {
  bucket        = "lr-20-pds-reg-input-${var.suffix}"
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "Input file storage for PDS practice supplementary data"
  }
}
