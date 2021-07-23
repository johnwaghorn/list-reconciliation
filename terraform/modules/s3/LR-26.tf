resource "aws_s3_bucket" "LR-26" {
  bucket        = "lr-26-access-logs-${var.suffix}"
  acl           = "log-delivery-write"
  force_destroy = var.force_destroy

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}
