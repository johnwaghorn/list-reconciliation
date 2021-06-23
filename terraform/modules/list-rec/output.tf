output "sqs_queue_name" {
  value = aws_sqs_queue.Patient_Records_Queue.name
}

output "sqs_queue_arn" {
  value = aws_sqs_queue.Patient_Records_Queue.arn
}

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

output "LR-12-lambda" {
  value = module.LR-12.LR-12-lambda
}

output "mock_pds_data" {
  value = aws_s3_bucket.mock-pds-data.bucket
}

output "LR_22_bucket" {
  value = aws_s3_bucket.LR-22.bucket
}