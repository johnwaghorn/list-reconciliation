output "mock_pds_data_bucket_arn" {
  value = aws_s3_bucket.mock_pds_data.arn
}

output "mock_pds_data_bucket_name" {
  value = aws_s3_bucket.mock_pds_data.bucket
}
