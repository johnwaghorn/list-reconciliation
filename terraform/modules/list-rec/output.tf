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

output "LR_02_Lambda" {
  value = module.LR-02.LR_02_lambda
}

output "LR_02_Lambda_arn" {
  value = module.LR-02.LR-02-lambda_arn
}

output "LR_07_Lambda" {
  value = module.LR-07.LR_07_lambda
}

output "LR_07_Lambda_arn" {
  value = module.LR-07.LR_07_lambda_arn
}

output "LR_08_Lambda" {
  value = module.LR-08.LR-08-lambda
}

output "LR_08_Lambda_arn" {
  value = module.LR-08.LR-08-lambda_arn
}

output "LR_09_Lambda" {
  value = module.LR-09.LR-09-lambda
}

output "LR_11_Lambda" {
  value = module.LR-11.LR_11_lambda
}

output "LR_11_Lambda_arn" {
  value = module.LR-11.LR_11_lambda_arn
}

output "LR_10_SFN" {
  value = module.LR-10.LR-11-sfn
}

output "LR_10_SFN_arn" {
  value = module.LR-10.LR-11-sfn_arn
}

output "Jobs_Table" {
  value = module.Jobs_Table.dynamo_table_name
}

output "Demographic_Table" {
  value = module.Demographics_Table.dynamo_table_name
}

output "InFlight_Table" {
  value = module.In_Flight_Table.dynamo_table_name
}

output "Errors_Table" {
  value = module.Errors_Table.dynamo_table_name
}

output "Demographics_Difference_Table" {
  value = module.Demographics_Differences_Table.dynamo_table_name
}

output "Jobs_Status_Table" {
  value = module.Jobs_Stats_Table.dynamo_table_name
}

output "Statuses_Table" {
  value = module.Statuses_Table.dynamo_table_name

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