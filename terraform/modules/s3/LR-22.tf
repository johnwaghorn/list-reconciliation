resource "aws_s3_bucket" "LR-22" {
  bucket        = "lr-22-pds-reg-output-${var.suffix}"
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "Output file storage for PDS practice extract files"
  }
}
