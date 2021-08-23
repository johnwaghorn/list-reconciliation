output "lr_02_lambda" {
  value = module.lr_02_validate_and_parse.LR_02_lambda
}

output "lr_02_lambda_arn" {
  value = module.lr_02_validate_and_parse.LR-02-lambda_arn
}

output "lr_04_lambda" {
  value = module.lr_04_feedback_failure.LR_04_lambda
}

output "lr_04_lambda_arn" {
  value = module.lr_04_feedback_failure.LR-04-lambda_arn
}

output "lr_07_lambda" {
  value = module.lr_07_pds_hydrate.lambda.function_name
}

output "lr_07_lambda_arn" {
  value = module.lr_07_pds_hydrate.lambda.arn
}

output "lr_08_lambda" {
  value = module.lr_08_demographic_comparison.LR-08-lambda
}

output "lr_08_lambda_arn" {
  value = module.lr_08_demographic_comparison.LR-08-lambda_arn
}

output "lr_09_lambda" {
  value = module.lr_09_scheduled_check.LR-09-lambda
}

output "lr_11_lambda" {
  value = module.lr_11_gp_registration_status.LR_11_lambda
}

output "lr_11_lambda_arn" {
  value = module.lr_11_gp_registration_status.LR_11_lambda_arn
}

output "lr_12_lambda" {
  value = module.lr_12_pds_registration_status.lambda.function_name
}

output "lr_12_lambda_arn" {
  value = module.lr_12_pds_registration_status.lambda.arn
}

output "lr_14_lambda" {
  value = module.lr_14_send_list_rec_results.LR-14-lambda
}

output "lr_14_lambda_arn" {
  value = module.lr_14_send_list_rec_results.LR-14-lambda_arn
}

output "lr_15_lambda" {
  value = module.lr_15_process_demo_diffs.LR-15-lambda
}

output "lr_15_lambda_arn" {
  value = module.lr_15_process_demo_diffs.LR-15-lambda_arn
}

output "lr_24_lambda" {
  value = module.lr_24_save_records_to_s3.LR-24-lambda
}

output "lr_24_lambda_arn" {
  value = module.lr_24_save_records_to_s3.LR-24-lambda_arn
}

output "lr_25_lambda" {
  value = module.lr_25_mesh_post_office.lambda.function_name
}

output "lr_25_lambda_arn" {
  value = module.lr_25_mesh_post_office.lambda.arn
}
