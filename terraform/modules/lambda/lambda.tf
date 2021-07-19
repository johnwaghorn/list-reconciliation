locals {
  lambda_name = {
    LR-02 = "LR_02_validate_and_parse"
    LR-07 = "LR_07_pds_hydrate"
    LR-08 = "LR_08_demographic_comparison"
    LR-09 = "LR_09_scheduled_check"
    LR-11 = "LR_11_gp_registration_status"
    LR-12 = "LR_12_pds_registration_status"
    LR-15 = "LR_15_process_demo_diffs"
    LR-21 = "LR_21_split_dps_extract"
  }
}

module "LR-02" {
  source                  = "./LR-02"
  lambda_name             = local.lambda_name.LR-02
  package_layer_arn       = aws_lambda_layer_version.package_layer.arn
  runtime                 = var.runtime
  source_bucket           = var.s3_buckets.LR-01.bucket
  lr_01_inbound_folder    = var.s3_buckets.LR-01.inbound_key
  patient_sqs_arn         = var.sqs.patient_records_queue.arn
  patient_sqs_name        = var.sqs.patient_records_queue.name
  demographics_table_arn  = var.dynamodb_tables.demographics.arn
  demographics_table_name = var.dynamodb_tables.demographics.name
  errors_table_arn        = var.dynamodb_tables.errors.arn
  errors_table_name       = var.dynamodb_tables.errors.name
  in_flight_table_arn     = var.dynamodb_tables.in_flight.arn
  in_flight_table_name    = var.dynamodb_tables.in_flight.name
  jobs_table_arn          = var.dynamodb_tables.jobs.arn
  jobs_table_name         = var.dynamodb_tables.jobs.name
  suffix                  = var.suffix
  lambda_handler          = var.lambda_handler
  dynamodb_kms_key        = var.dynamodb_kms_key
}

module "LR-07" {
  source                   = "./LR-07"
  lambda_name              = local.lambda_name.LR-07
  package_layer_arn        = aws_lambda_layer_version.package_layer.arn
  runtime                  = var.runtime
  lambda_timeout           = var.lambda_timeout
  lr_08_lambda             = module.LR-08.LR-08-lambda_arn
  patient_sqs_arn          = var.sqs.patient_records_queue.arn
  demographics_table_arn   = var.dynamodb_tables.demographics.arn
  demographics_table_name  = var.dynamodb_tables.demographics.name
  errors_table_arn         = var.dynamodb_tables.errors.arn
  errors_table_name        = var.dynamodb_tables.errors.name
  mock_pds_data_bucket_arn = var.mock_pds_data_bucket.arn
  pds_url                  = "s3://${var.mock_pds_data_bucket.name}/${var.pds_url}"
  suffix                   = var.suffix
  lambda_handler           = var.lambda_handler
  dynamodb_kms_key         = var.dynamodb_kms_key
}

module "LR-08" {
  source                              = "./LR-08"
  lambda_name                         = local.lambda_name.LR-08
  runtime                             = var.runtime
  lambda_timeout                      = var.lambda_timeout
  package_layer_arn                   = aws_lambda_layer_version.package_layer.arn
  demographics_table_arn              = var.dynamodb_tables.demographics.arn
  demographics_table_name             = var.dynamodb_tables.demographics.name
  errors_table_arn                    = var.dynamodb_tables.errors.arn
  errors_table_name                   = var.dynamodb_tables.errors.name
  demographics_differences_table_name = var.dynamodb_tables.demographics_differences.name
  demographics_differences_table_arn  = var.dynamodb_tables.demographics_differences.arn
  suffix                              = var.suffix
  lambda_handler                      = var.lambda_handler
  dynamodb_kms_key                    = var.dynamodb_kms_key
}

module "LR-09" {
  source                  = "./LR-09"
  lambda_name             = local.lambda_name.LR-09
  runtime                 = var.runtime
  lambda_timeout          = var.lambda_timeout
  package_layer_arn       = aws_lambda_layer_version.package_layer.arn
  lr_10_step_function_arn = var.step_functions.lr_10_registration_orchestration.arn
  demographics_table_arn  = var.dynamodb_tables.demographics.arn
  demographics_table_name = var.dynamodb_tables.demographics.name
  jobs_table_arn          = var.dynamodb_tables.jobs.arn
  jobs_table_name         = var.dynamodb_tables.jobs.name
  job_stats_table_arn     = var.dynamodb_tables.jobs_stats.arn
  job_stats_table_name    = var.dynamodb_tables.jobs_stats.name
  in_flight_table_arn     = var.dynamodb_tables.in_flight.arn
  in_flight_table_name    = var.dynamodb_tables.in_flight.name
  errors_table_arn        = var.dynamodb_tables.errors.arn
  errors_table_name       = var.dynamodb_tables.errors.name
  suffix                  = var.suffix
  lambda_handler          = var.lambda_handler
  dynamodb_kms_key        = var.dynamodb_kms_key
}

module "LR-11" {
  source                          = "./LR-11"
  lambda_name                     = local.lambda_name.LR-11
  runtime                         = var.runtime
  lambda_timeout                  = var.lambda_timeout
  package_layer_arn               = aws_lambda_layer_version.package_layer.arn
  registrations_output_bucket_arn = var.s3_buckets.LR-13.arn
  registrations_output_bucket     = var.s3_buckets.LR-13.bucket
  demographics_table_arn          = var.dynamodb_tables.demographics.arn
  demographics_table_name         = var.dynamodb_tables.demographics.name
  jobs_table_arn                  = var.dynamodb_tables.jobs.arn
  jobs_table_name                 = var.dynamodb_tables.jobs.name
  job_stats_table_arn             = var.dynamodb_tables.jobs_stats.arn
  job_stats_table_name            = var.dynamodb_tables.jobs_stats.name
  errors_table_arn                = var.dynamodb_tables.errors.arn
  errors_table_name               = var.dynamodb_tables.errors.name
  suffix                          = var.suffix
  lambda_handler                  = var.lambda_handler
  dynamodb_kms_key                = var.dynamodb_kms_key
}

module "LR-12" {
  source                                = "./LR-12"
  lambda_name                           = local.lambda_name.LR-12
  runtime                               = var.runtime
  lambda_timeout                        = var.lambda_timeout
  package_layer_arn                     = aws_lambda_layer_version.package_layer.arn
  registrations_output_bucket_arn       = var.s3_buckets.LR-13.arn
  registrations_output_bucket           = var.s3_buckets.LR-13.bucket
  pds_practice_registrations_bucket_arn = var.s3_buckets.LR-22.arn
  pds_practice_registrations_bucket     = var.s3_buckets.LR-22.bucket
  demographics_table_arn                = var.dynamodb_tables.demographics.arn
  demographics_table_name               = var.dynamodb_tables.demographics.name
  jobs_table_arn                        = var.dynamodb_tables.jobs.arn
  jobs_table_name                       = var.dynamodb_tables.jobs.name
  job_stats_table_arn                   = var.dynamodb_tables.jobs_stats.arn
  job_stats_table_name                  = var.dynamodb_tables.jobs_stats.name
  errors_table_arn                      = var.dynamodb_tables.errors.arn
  errors_table_name                     = var.dynamodb_tables.errors.name
  mock_pds_data_bucket_arn              = var.mock_pds_data_bucket.arn
  pds_url                               = "s3://${var.mock_pds_data_bucket.name}/${var.pds_url}"
  pds_api_retries                       = var.pds_api_retries
  suffix                                = var.suffix
  lambda_handler                        = var.lambda_handler
  dynamodb_kms_key                      = var.dynamodb_kms_key
}

module "LR-15" {
  source                              = "./LR-15"
  lambda_name                         = local.lambda_name.LR-15
  runtime                             = var.runtime
  lambda_timeout                      = var.lambda_timeout
  package_layer_arn                   = aws_lambda_layer_version.package_layer.arn
  mesh_send_bucket_arn                = var.s3_buckets.LR-23.arn
  mesh_send_bucket                    = var.s3_buckets.LR-23.bucket
  registrations_output_bucket_arn     = var.s3_buckets.LR-13.arn
  registrations_output_bucket         = var.s3_buckets.LR-13.bucket
  demographics_table_arn              = var.dynamodb_tables.demographics.arn
  demographics_table_name             = var.dynamodb_tables.demographics.name
  jobs_table_arn                      = var.dynamodb_tables.jobs.arn
  jobs_table_name                     = var.dynamodb_tables.jobs.name
  job_stats_table_arn                 = var.dynamodb_tables.jobs_stats.arn
  job_stats_table_name                = var.dynamodb_tables.jobs_stats.name
  errors_table_arn                    = var.dynamodb_tables.errors.arn
  errors_table_name                   = var.dynamodb_tables.errors.name
  demographics_differences_table_name = var.dynamodb_tables.demographics_differences.name
  demographics_differences_table_arn  = var.dynamodb_tables.demographics_differences.arn
  suffix                              = var.suffix
  lambda_handler                      = var.lambda_handler
  dynamodb_kms_key                    = var.dynamodb_kms_key
}

module "LR-21" {
  source                      = "./LR-21"
  lambda_name                 = local.lambda_name.LR-21
  runtime                     = var.runtime
  package_layer_arn           = aws_lambda_layer_version.package_layer.arn
  supplementary-input-bucket  = var.s3_buckets.LR-20.bucket
  supplementary-output-bucket = var.s3_buckets.LR-22.bucket
  errors_table_arn            = var.dynamodb_tables.errors.arn
  errors_table_name           = var.dynamodb_tables.errors.name
  suffix                      = var.suffix
  lambda_handler              = var.lambda_handler
  dynamodb_kms_key            = var.dynamodb_kms_key
}
