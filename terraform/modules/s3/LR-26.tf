resource "aws_s3_bucket" "LR-26" {
  bucket = "lr-26-access-logs-${var.suffix}"
  acl    = "log-delivery-write"
}