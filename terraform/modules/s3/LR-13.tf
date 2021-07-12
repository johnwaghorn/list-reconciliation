resource "aws_s3_bucket" "LR-13" {
  bucket        = "lr-13-reg-diffs-output-${var.suffix}"
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "Output file storage for LR-11 LR-12 and LR-14"
  }
}
