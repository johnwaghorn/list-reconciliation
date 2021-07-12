output "region" {
  value = "eu-west-2"
}

output "lr_01_bucket" {
  value = module.list_rec.LR_01_Bucket
}

output "lr_01_bucket_inbound" {
  value = module.list_rec.LR_01_Bucket_inbound
}

output "lr_01_bucket_pass" {
  value = module.list_rec.LR_01_Bucket_pass
}

output "lr_01_bucket_fail" {
  value = module.list_rec.LR_01_Bucket_fail
}

output "lr_01_bucket_retry" {
  value = module.list_rec.LR_01_Bucket_retry
}

output "patients_queue" {
  value = module.list_rec.sqs_queue_name
}

output "lr_02_lambda" {
  value = module.list_rec.LR_02_Lambda
}

output "lr_02_lambda_arn" {
  value = module.list_rec.LR_02_Lambda_arn
}

output "lr_07_lambda" {
  value = module.list_rec.LR_07_Lambda
}

output "lr_07_lambda_arn" {
  value = module.list_rec.LR_07_Lambda_arn
}

output "lr_08_lambda" {
  value = module.list_rec.LR_08_Lambda
}

output "lr_08_lambda_arn" {
  value = module.list_rec.LR_08_Lambda_arn
}

output "lr_09_lambda" {
  value = module.list_rec.LR_09_Lambda
}

output "lr_10_sfn" {
  value = module.list_rec.LR_10_SFN
}

output "lr_10_sfn_arn" {
  value = module.list_rec.LR_10_SFN_arn
}

output "lr_11_lambda" {
  value = module.list_rec.LR_11_Lambda
}

output "lr_11_lambda_arn" {
  value = module.list_rec.LR_11_Lambda_arn
}

output "jobs_table" {
  value = module.jobs_table.dynamo_table_name
}

output "demographic_table" {
  value = module.demographics_table.dynamo_table_name
}

output "inflight_table" {
  value = module.in_flight_table.dynamo_table_name
}

output "errors_table" {
  value = module.errors_table.dynamo_table_name
}

output "demographics_difference_table" {
  value = module.demographics_differences_table.dynamo_table_name
}

output "jobs_stats_table" {
  value = module.jobs_stats_table.dynamo_table_name
}

output "statuses_table" {
  value = module.statuses_table.dynamo_table_name
}

output "lr_12_lambda" {
  value = module.list_rec.LR-12-lambda
}

output "mock_pds_data" {
  value = module.list_rec.mock_pds_data
}

output "lr_13_bucket" {
  value = module.list_rec.LR_13_bucket
}

output "lr_22_bucket" {
  value = module.list_rec.LR_22_bucket
}

output "lr_15_lambda" {
  value = module.list_rec.LR-15-lambda
}
