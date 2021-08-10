output "LR_01_Bucket" {
  value = aws_s3_bucket.LR-01.bucket
}

output "LR_01_Bucket_pass" {
  value = aws_s3_bucket_object.pass.key
}

output "LR_01_Bucket_fail" {
  value = aws_s3_bucket_object.fail.key
}

output "LR_01_Bucket_inbound" {
  value = aws_s3_bucket_object.inbound.key
}

output "LR_01_Bucket_retry" {
  value = aws_s3_bucket_object.retry.key
}

output "buckets" {
  value = {
    LR-01 = {
      bucket      = aws_s3_bucket.LR-01.id
      arn         = aws_s3_bucket.LR-01.arn
      pass_key    = aws_s3_bucket_object.pass.key
      fail_key    = aws_s3_bucket_object.fail.key
      inbound_key = aws_s3_bucket_object.inbound.key
      retry_key   = aws_s3_bucket_object.retry.key
    }
    LR-06 = {
      bucket = aws_s3_bucket.LR-06.id
      arn    = aws_s3_bucket.LR-06.arn
    }
    LR-13 = {
      bucket = aws_s3_bucket.LR-13.id
      arn    = aws_s3_bucket.LR-13.arn
    }
    LR-20 = {
      bucket = aws_s3_bucket.LR-20.id
      arn    = aws_s3_bucket.LR-20.arn
    }
    LR-22 = {
      bucket = aws_s3_bucket.LR-22.id
      arn    = aws_s3_bucket.LR-22.arn
    }
    LR-26 = {
      bucket = aws_s3_bucket.LR-26.id
      arn    = aws_s3_bucket.LR-26.arn
    }
    mesh_bucket = {
      bucket = var.suffix == "prod" ? data.aws_s3_bucket.mesh_bucket[0].id : aws_s3_bucket.mesh_dummy[0].id
      arn    = var.suffix == "prod" ? data.aws_s3_bucket.mesh_bucket[0].arn : aws_s3_bucket.mesh_dummy[0].arn
    }
  }
}
