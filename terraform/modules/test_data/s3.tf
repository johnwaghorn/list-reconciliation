#tfsec:ignore:custom-custom-lr-all-buckets-log tfsec:ignore:aws-s3-enable-bucket-logging tfsec:ignore:aws-s3-enable-versioning
resource "aws_s3_bucket" "mock_pds_data" {
  bucket        = "mock-pds-data-${var.suffix}"
  acl           = "private"
  force_destroy = true

  tags = {
    Name = "File storage for PDS mock api data"
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = var.kms_key_arn
        sse_algorithm     = "aws:kms"
      }
      bucket_key_enabled = true
    }
  }
}

resource "aws_s3_bucket_object" "upload-mock-pds-data" {
  bucket = aws_s3_bucket.mock_pds_data.id
  key    = "pds_api_data.csv"
  acl    = "private"
  source = "../../../test/unittests/lambdas/data/pds_api_data.csv"
  etag   = filemd5("../../../test/unittests/lambdas/data/pds_api_data.csv")
}

resource "aws_s3_bucket_object" "upload-test-pds-registration-data-1" {
  bucket = var.LR_22_bucket
  key    = "Y123451.csv"
  acl    = "private"
  source = "../../../test/unittests/lambdas/data/Y123451.csv"
  etag   = filemd5("../../../test/unittests/lambdas/data/Y123451.csv")
}

resource "aws_s3_bucket_object" "upload-test-pds-registration-data-2" {
  bucket = var.LR_22_bucket
  key    = "Y123452.csv"
  acl    = "private"
  source = "../../../test/unittests/lambdas/data/Y123452.csv"
  etag   = filemd5("../../../test/unittests/lambdas/data/Y123452.csv")
}

resource "aws_s3_bucket_object" "upload-test-pds-registration-data-3" {
  bucket = var.LR_22_bucket
  key    = "Y12345.csv"
  acl    = "private"
  source = "../../../test/unittests/lambdas/data/Y12345.csv"
  etag   = filemd5("../../../test/unittests/lambdas/data/Y12345.csv")
}
