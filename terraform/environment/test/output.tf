output "lr_01_bucket" {
  value = module.List-Recon.LR_01_Bucket
}

output "lr_01_bucket_inbound" {
  value = module.List-Recon.LR_01_Bucket_inbound
}

output "lr_01_bucket_pass" {
  value = module.List-Recon.LR_01_Bucket_pass
}

output "lr_01_bucket_fail" {
  value = module.List-Recon.LR_01_Bucket_fail
}

output "lr_01_bucket_retry" {
  value = module.List-Recon.LR_01_Bucket_retry
}

output "patients_queue" {
  value = module.List-Recon.sqs_queue_name
}

output "lr_02_lambda" {
  value = module.List-Recon.LR_02_Lambda
}

output "lr_02_lambda_arn" {
  value = module.List-Recon.LR_02_Lambda_arn
}

output "lr_07_lambda" {
  value = module.List-Recon.LR_07_Lambda
}

output "lr_07_lambda_arn" {
  value = module.List-Recon.LR_07_Lambda_arn
}

output "lr_08_lambda" {
  value = module.List-Recon.LR_08_Lambda
}

output "lr_08_lambda_arn" {
  value = module.List-Recon.LR_08_Lambda_arn
}

output "lr_09_lambda" {
  value = module.List-Recon.LR_09_Lambda
}

output "lr_10_sfn" {
  value = module.List-Recon.LR_10_SFN
}

output "lr_10_sfn_arn" {
  value = module.List-Recon.LR_10_SFN_arn
}

output "lr_11_lambda" {
  value = module.List-Recon.LR_11_Lambda
}

output "lr_11_lambda_arn" {
  value = module.List-Recon.LR_11_Lambda_arn
}

output "region" {
  value = var.region
}

output "jobs_table" {
  value = module.List-Recon.Jobs_Table
}

output "demographic_table" {
  value = module.List-Recon.Demographic_Table
}

output "inflight_table" {
  value = module.List-Recon.InFlight_Table
}

output "errors_table" {
  value = module.List-Recon.Errors_Table
}

output "demographics_difference_table" {
  value = module.List-Recon.Demographics_Difference_Table
}

output "jobs_Status_table" {
  value = module.List-Recon.Jobs_Status_Table
}

output "statuses_table" {
  value = module.List-Recon.Statuses_Table
}

output "lr_12_lambda" {
  value = module.List-Recon.LR-12-lambda
}

output "mock_pds_data" {
  value = module.List-Recon.mock_pds_data
}

output "lr_22_bucket" {
  value = module.List-Recon.LR_22_bucket
}

output "lr_13_bucket" {
  value = module.List-Recon.LR_13_bucket
}

output "lr_15_lambda" {
  value = module.List-Recon.LR-15-lambda
}