output "region" {
  value = "eu-west-2"
}

output "lr_01_bucket" {
  value = module.list-rec.LR_01_Bucket
}

output "lr_01_bucket_inbound" {
  value = module.list-rec.LR_01_Bucket_inbound
}

output "lr_01_bucket_pass" {
  value = module.list-rec.LR_01_Bucket_pass
}

output "lr_01_bucket_fail" {
  value = module.list-rec.LR_01_Bucket_fail
}

output "lr_01_bucket_retry" {
  value = module.list-rec.LR_01_Bucket_retry
}

output "patients_queue" {
  value = module.list-rec.sqs_queue_name
}

output "lr_02_lambda" {
  value = module.list-rec.LR_02_Lambda
}

output "lr_02_lambda_arn" {
  value = module.list-rec.LR_02_Lambda_arn
}

output "lr_07_lambda" {
  value = module.list-rec.LR_07_Lambda
}

output "lr_07_lambda_arn" {
  value = module.list-rec.LR_07_Lambda_arn
}

output "lr_08_lambda" {
  value = module.list-rec.LR_08_Lambda
}

output "lr_08_lambda_arn" {
  value = module.list-rec.LR_08_Lambda_arn
}

output "lr_09_lambda" {
  value = module.list-rec.LR_09_Lambda
}

output "lr_10_sfn" {
  value = module.list-rec.LR_10_SFN
}

output "lr_10_sfn_arn" {
  value = module.list-rec.LR_10_SFN_arn
}

output "lr_11_lambda" {
  value = module.list-rec.LR_11_Lambda
}

output "lr_11_lambda_arn" {
  value = module.list-rec.LR_11_Lambda_arn
}

output "jobs_table" {
  value = module.list-rec.Jobs_Table
}

output "demographic_table" {
  value = module.list-rec.Demographic_Table
}

output "inflight_table" {
  value = module.list-rec.InFlight_Table
}

output "errors_table" {
  value = module.list-rec.Errors_Table
}

output "demographics_difference_table" {
  value = module.list-rec.Demographics_Difference_Table
}

output "jobs_Status_table" {
  value = module.list-rec.Jobs_Status_Table
}

output "statuses_table" {
  value = module.list-rec.Statuses_Table
}

output "lr_12_lambda" {
  value = module.list-rec.LR-12-lambda
}

output "mock_pds_data" {
  value = module.list-rec.mock_pds_data
}

output "lr_22_bucket" {
  value = module.list-rec.LR_22_bucket
}

output "lr_13_bucket" {
  value = module.list-rec.LR_13_bucket
}

output "lr_15_lambda" {
  value = module.list-rec.LR-15-lambda
}
