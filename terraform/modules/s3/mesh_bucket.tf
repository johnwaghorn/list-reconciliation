data "aws_s3_bucket" "mesh_bucket" {
  count  = var.suffix == "prod" ? 1 : 0
  bucket = "list-rec-${var.suffix}-mesh"
}

resource "aws_s3_bucket" "mesh_dummy" {
  count         = var.suffix == "prod" ? 0 : 1
  bucket        = "mesh-dummy-${var.suffix}"
  acl           = "private"
  force_destroy = var.force_destroy

  tags = {
    Name = "Dummy mesh bucket for dev environments"
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = var.mesh_kms_key
        sse_algorithm     = "aws:kms"
      }
      bucket_key_enabled = true
    }
  }

  versioning {
    enabled = true
  }

  logging {
    target_bucket = aws_s3_bucket.LR-26.id
    target_prefix = "mesh-dummy-${var.suffix}/"
  }
}
