output "environment" {
  value = local.environment
}

output "lr_01_bucket" {
  value = module.lr_01_gp_extract_input.bucket.bucket
}

output "lr_06_bucket" {
  value = module.lr_06_patient_records.bucket.bucket
}

output "lr_13_bucket" {
  value = module.lr_13_reg_diffs_output.bucket.bucket
}

output "lr_20_bucket" {
  value = module.lr_20_pds_reg_input.bucket.bucket
}

output "lr_22_bucket" {
  value = module.lr_22_pds_reg_output.bucket.bucket
}

output "lr_26_bucket" {
  value = module.lr_26_access_logs.bucket.bucket
}

output "mesh_bucket" {
  value = module.mesh_bucket.bucket.bucket
}

output "lr_send_email_bucket" {
  value = module.lr_send_email_bucket.bucket.bucket
}

output "lr_02_lambda" {
  value = module.lr_02_validate_and_parse.lambda.function_name
}

output "lr_02_lambda_arn" {
  value = module.lr_02_validate_and_parse.lambda.arn
}

output "lr_04_lambda" {
  value = module.lr_04_feedback_failure.lambda.function_name
}

output "lr_04_lambda_arn" {
  value = module.lr_04_feedback_failure.lambda.arn
}

output "lr_07_lambda" {
  value = module.lr_07_pds_hydrate.lambda.function_name
}

output "lr_07_lambda_arn" {
  value = module.lr_07_pds_hydrate.lambda.arn
}

output "lr_08_lambda" {
  value = module.lr_08_demographic_comparison.lambda.function_name
}

output "lr_08_lambda_arn" {
  value = module.lr_08_demographic_comparison.lambda.arn
}

output "lr_09_lambda" {
  value = module.lr_09_scheduled_check.lambda.function_name
}

output "lr_09_lambda_arn" {
  value = module.lr_09_scheduled_check.lambda.arn
}

output "lr_11_lambda" {
  value = module.lr_11_gp_registration_status.lambda.function_name
}

output "lr_11_lambda_arn" {
  value = module.lr_11_gp_registration_status.lambda.arn
}

output "lr_12_lambda" {
  value = module.lr_12_pds_registration_status.lambda.function_name
}

output "lr_12_lambda_arn" {
  value = module.lr_12_pds_registration_status.lambda.arn
}

output "lr_15_lambda" {
  value = module.lr_15_process_demo_diffs.lambda.function_name
}

output "lr_15_lambda_arn" {
  value = module.lr_15_process_demo_diffs.lambda.arn
}

output "lr_24_lambda" {
  value = module.lr_24_save_records_to_s3.lambda.function_name
}

output "lr_24_lambda_arn" {
  value = module.lr_24_save_records_to_s3.lambda.arn
}

output "lr_25_lambda" {
  value = module.lr_25_mesh_post_office.lambda.function_name
}

output "lr_25_lambda_arn" {
  value = module.lr_25_mesh_post_office.lambda.arn
}

output "lr_10_sfn" {
  value = module.lr_10_registration_orchestration.step_function.name
}

output "lr_10_sfn_arn" {
  value = module.lr_10_registration_orchestration.step_function.arn
}

output "lambda_send_email_lambda" {
  value = module.lambda_send_email.lambda.function_name
}

output "lambda_send_email_lambda_arn" {
  value = module.lambda_send_email.lambda.arn
}

output "jobs_table" {
  value = module.lr_03_jobs.table.name
}

output "jobs_stats_table" {
  value = module.lr_28_jobs_stats.table.name
}

output "in_flight_table" {
  value = module.lr_29_in_flight.table.name
}

output "demographics_table" {
  value = module.lr_30_demographics.table.name
}

output "demographics_differences_table" {
  value = module.lr_31_demographics_differences.table.name
}

output "mesh_inbound" {
  value = "inbound_${try(local.mesh_mappings[local.environment][0].id, local.mesh_mappings["default"][0].id)}"
}

output "pds_url" {
  value = try(local.pds_fhir_api_url[local.environment], local.pds_fhir_api_url["default"])
}
