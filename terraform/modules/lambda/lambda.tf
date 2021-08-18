locals {
  lambda_name = {
    LR-02 = "LR_02_validate_and_parse"
    LR-04 = "LR_04_feedback_failure"
    LR-07 = "LR_07_pds_hydrate"
    LR-08 = "LR_08_demographic_comparison"
    LR-09 = "LR_09_scheduled_check"
    LR-11 = "LR_11_gp_registration_status"
    LR-12 = "LR_12_pds_registration_status"
    LR-14 = "LR_14_send_list_rec_results"
    LR-15 = "LR_15_process_demo_diffs"
    LR-24 = "LR_24_save_records_to_s3"
    LR-21 = "LR_21_split_dps_extract"
    lr_25 = "LR_25_mesh_post_office"
    lr_27 = "LR_27_job_cleanup"
  }
}

module "LR-02" {
  source = "./LR-02"

  lambda_name           = local.lambda_name.LR-02
  package_layer_arn     = aws_lambda_layer_version.package_layer.arn
  runtime               = var.runtime
  source_bucket         = var.s3_buckets.LR-01.bucket
  source_bucket_arn     = var.s3_buckets.LR-01.arn
  lr_01_inbound_folder  = var.s3_buckets.LR-01.inbound_key
  lr_01_failed_folder   = var.s3_buckets.LR-01.fail_key
  lr_06_bucket          = var.s3_buckets.LR-06.bucket
  lr_04_lambda_arn      = module.LR-04.LR-04-lambda_arn
  lr_24_lambda_arn      = module.LR-24.LR-24-lambda_arn
  in_flight_table_arn   = var.dynamodb_tables.in_flight.arn
  in_flight_table_name  = var.dynamodb_tables.in_flight.name
  jobs_table_arn        = var.dynamodb_tables.jobs.arn
  jobs_table_name       = var.dynamodb_tables.jobs.name
  suffix                = var.suffix
  lambda_handler        = var.lambda_handler
  cloudwatch_kms_key    = var.cloudwatch_kms_key
  dynamodb_kms_key      = var.dynamodb_kms_key
  s3_kms_key            = var.s3_kms_key
  log_retention_in_days = var.log_retention_in_days
}

module "LR-04" {
  source = "./LR-04"

  lambda_name           = local.lambda_name.LR-04
  package_layer_arn     = aws_lambda_layer_version.package_layer.arn
  runtime               = var.runtime
  source_bucket         = var.s3_buckets.LR-01.bucket
  source_bucket_arn     = var.s3_buckets.LR-01.arn
  suffix                = var.suffix
  lambda_handler        = var.lambda_handler
  cloudwatch_kms_key    = var.cloudwatch_kms_key
  s3_kms_key            = var.s3_kms_key
  log_retention_in_days = var.log_retention_in_days
  email_ssm             = var.email_ssm_prefix
  pcse_email            = var.pcse_email
  listrec_email         = var.listrec_email
  ssm_kms_key           = var.ssm_kms_key
}

module "LR-07" {
  source = "./LR-07"

  lambda_name                          = local.lambda_name.LR-07
  package_layer_arn                    = aws_lambda_layer_version.package_layer.arn
  runtime                              = var.runtime
  lambda_timeout                       = var.lambda_timeout
  lr_08_lambda                         = module.LR-08.LR-08-lambda_arn
  demographics_table_arn               = var.dynamodb_tables.demographics.arn
  demographics_table_name              = var.dynamodb_tables.demographics.name
  lr_06_bucket_arn                     = var.s3_buckets.LR-06.arn
  lr_06_bucket                         = var.s3_buckets.LR-06.bucket
  mock_pds_data_bucket_arn             = var.mock_pds_data_bucket.arn
  suffix                               = var.suffix
  lambda_handler                       = var.lambda_handler
  cloudwatch_kms_key                   = var.cloudwatch_kms_key
  dynamodb_kms_key                     = var.dynamodb_kms_key
  s3_kms_key                           = var.s3_kms_key
  log_retention_in_days                = var.log_retention_in_days
  ssm_kms_key                          = var.ssm_kms_key
  pds_ssm_prefix                       = var.pds_ssm_prefix
  pds_ssm_access_token                 = var.pds_ssm_access_token
  pds_base_url                         = var.pds_base_url
  lr_07_reserved_concurrent_executions = var.lr_07_reserved_concurrent_executions
}

module "LR-08" {
  source = "./LR-08"

  lambda_name                         = local.lambda_name.LR-08
  runtime                             = var.runtime
  lambda_timeout                      = var.lambda_timeout
  package_layer_arn                   = aws_lambda_layer_version.package_layer.arn
  demographics_table_arn              = var.dynamodb_tables.demographics.arn
  demographics_table_name             = var.dynamodb_tables.demographics.name
  demographics_differences_table_name = var.dynamodb_tables.demographics_differences.name
  demographics_differences_table_arn  = var.dynamodb_tables.demographics_differences.arn
  suffix                              = var.suffix
  lambda_handler                      = var.lambda_handler
  cloudwatch_kms_key                  = var.cloudwatch_kms_key
  dynamodb_kms_key                    = var.dynamodb_kms_key
  s3_kms_key                          = var.s3_kms_key
  log_retention_in_days               = var.log_retention_in_days
}

module "LR-09" {
  source = "./LR-09"

  lambda_name                     = local.lambda_name.LR-09
  runtime                         = var.runtime
  lambda_timeout                  = var.lambda_timeout
  package_layer_arn               = aws_lambda_layer_version.package_layer.arn
  lr_10_step_function_arn         = var.step_functions.lr_10_registration_orchestration.arn
  demographics_table_arn          = var.dynamodb_tables.demographics.arn
  demographics_table_name         = var.dynamodb_tables.demographics.name
  jobs_table_arn                  = var.dynamodb_tables.jobs.arn
  jobs_table_name                 = var.dynamodb_tables.jobs.name
  job_stats_table_arn             = var.dynamodb_tables.jobs_stats.arn
  job_stats_table_name            = var.dynamodb_tables.jobs_stats.name
  in_flight_table_arn             = var.dynamodb_tables.in_flight.arn
  in_flight_table_name            = var.dynamodb_tables.in_flight.name
  suffix                          = var.suffix
  lambda_handler                  = var.lambda_handler
  cloudwatch_kms_key              = var.cloudwatch_kms_key
  dynamodb_kms_key                = var.dynamodb_kms_key
  s3_kms_key                      = var.s3_kms_key
  log_retention_in_days           = var.log_retention_in_days
  lr_09_event_schedule_expression = var.lr_09_event_schedule_expression
}

module "LR-11" {
  source = "./LR-11"

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
  suffix                          = var.suffix
  lambda_handler                  = var.lambda_handler
  cloudwatch_kms_key              = var.cloudwatch_kms_key
  dynamodb_kms_key                = var.dynamodb_kms_key
  s3_kms_key                      = var.s3_kms_key
  log_retention_in_days           = var.log_retention_in_days
}

module "LR-12" {
  source = "./LR-12"

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
  mock_pds_data_bucket_arn              = var.mock_pds_data_bucket.arn
  pds_api_retries                       = var.pds_api_retries
  suffix                                = var.suffix
  lambda_handler                        = var.lambda_handler
  cloudwatch_kms_key                    = var.cloudwatch_kms_key
  dynamodb_kms_key                      = var.dynamodb_kms_key
  s3_kms_key                            = var.s3_kms_key
  log_retention_in_days                 = var.log_retention_in_days
  ssm_kms_key                           = var.ssm_kms_key
  pds_ssm_prefix                        = var.pds_ssm_prefix
  pds_base_url                          = var.pds_base_url
  pds_ssm_access_token                  = var.pds_ssm_access_token
}

module "LR-14" {
  source = "./LR-14"

  lambda_name                         = local.lambda_name.LR-14
  runtime                             = var.runtime
  lambda_timeout                      = var.lambda_timeout
  package_layer_arn                   = aws_lambda_layer_version.package_layer.arn
  mesh_send_bucket_arn                = var.s3_buckets.mesh_bucket.arn
  mesh_send_bucket                    = var.s3_buckets.mesh_bucket.bucket
  registrations_output_bucket_arn     = var.s3_buckets.LR-13.arn
  registrations_output_bucket         = var.s3_buckets.LR-13.bucket
  jobs_table_arn                      = var.dynamodb_tables.jobs.arn
  jobs_table_name                     = var.dynamodb_tables.jobs.name
  job_stats_table_arn                 = var.dynamodb_tables.jobs_stats.arn
  job_stats_table_name                = var.dynamodb_tables.jobs_stats.name
  demographics_differences_table_name = var.dynamodb_tables.demographics_differences.name
  demographics_differences_table_arn  = var.dynamodb_tables.demographics_differences.arn
  suffix                              = var.suffix
  lambda_handler                      = var.lambda_handler
  cloudwatch_kms_key                  = var.cloudwatch_kms_key
  dynamodb_kms_key                    = var.dynamodb_kms_key
  s3_kms_key                          = var.s3_kms_key
  ssm_kms_key                         = var.ssm_kms_key
  mesh_kms_key                        = var.mesh_kms_key
  log_retention_in_days               = var.log_retention_in_days
  mesh_ssm                            = var.mesh_ssm_prefix
  email_ssm                           = var.email_ssm_prefix
  pcse_email                          = var.pcse_email
  listrec_email                       = var.listrec_email
  send_emails                         = var.send_emails
}

module "LR-15" {
  source = "./LR-15"

  lambda_name                         = local.lambda_name.LR-15
  runtime                             = var.runtime
  lambda_timeout                      = var.lambda_timeout
  package_layer_arn                   = aws_lambda_layer_version.package_layer.arn
  mesh_send_bucket_arn                = var.s3_buckets.mesh_bucket.arn
  mesh_send_bucket                    = var.s3_buckets.mesh_bucket.bucket
  registrations_output_bucket_arn     = var.s3_buckets.LR-13.arn
  registrations_output_bucket         = var.s3_buckets.LR-13.bucket
  demographics_table_arn              = var.dynamodb_tables.demographics.arn
  demographics_table_name             = var.dynamodb_tables.demographics.name
  jobs_table_arn                      = var.dynamodb_tables.jobs.arn
  jobs_table_name                     = var.dynamodb_tables.jobs.name
  job_stats_table_arn                 = var.dynamodb_tables.jobs_stats.arn
  job_stats_table_name                = var.dynamodb_tables.jobs_stats.name
  demographics_differences_table_name = var.dynamodb_tables.demographics_differences.name
  demographics_differences_table_arn  = var.dynamodb_tables.demographics_differences.arn
  suffix                              = var.suffix
  lambda_handler                      = var.lambda_handler
  cloudwatch_kms_key                  = var.cloudwatch_kms_key
  dynamodb_kms_key                    = var.dynamodb_kms_key
  s3_kms_key                          = var.s3_kms_key
  mesh_kms_key                        = var.mesh_kms_key
  log_retention_in_days               = var.log_retention_in_days
  ssm_kms_key                         = var.ssm_kms_key
  mesh_ssm                            = var.mesh_ssm_prefix
}

module "LR-21" {
  source = "./LR-21"

  lambda_name                     = local.lambda_name.LR-21
  runtime                         = var.runtime
  package_layer_arn               = aws_lambda_layer_version.package_layer.arn
  supplementary_input_bucket      = var.s3_buckets.LR-20.bucket
  supplementary_input_bucket_arn  = var.s3_buckets.LR-20.arn
  supplementary_output_bucket     = var.s3_buckets.LR-22.bucket
  supplementary_output_bucket_arn = var.s3_buckets.LR-22.arn
  suffix                          = var.suffix
  lambda_handler                  = var.lambda_handler
  cloudwatch_kms_key              = var.cloudwatch_kms_key
  s3_kms_key                      = var.s3_kms_key
  log_retention_in_days           = var.log_retention_in_days
}

module "LR-24" {
  source = "./LR-24"

  lambda_name           = local.lambda_name.LR-24
  package_layer_arn     = aws_lambda_layer_version.package_layer.arn
  runtime               = var.runtime
  lambda_timeout        = var.lambda_timeout
  suffix                = var.suffix
  lr-06-bucket          = var.s3_buckets.LR-06.bucket
  lr-06-bucket_arn      = var.s3_buckets.LR-06.arn
  lambda_handler        = var.lambda_handler
  cloudwatch_kms_key    = var.cloudwatch_kms_key
  s3_kms_key            = var.s3_kms_key
  log_retention_in_days = var.log_retention_in_days
}

module "lr_25" {
  source = "./LR_25_mesh_post_office"

  lambda_name                     = local.lambda_name.lr_25
  package_layer_arn               = aws_lambda_layer_version.package_layer.arn
  runtime                         = var.runtime
  suffix                          = var.suffix
  mesh_kms_key_alias              = var.mesh_kms_key_alias
  mesh_post_office_open           = var.mesh_post_office_open
  mesh_post_office_mappings       = var.mesh_post_office_mappings
  cloudwatch_kms_key              = var.cloudwatch_kms_key
  s3_kms_key                      = var.s3_kms_key
  log_retention_in_days           = var.log_retention_in_days
  lr_25_event_schedule_expression = var.lr_25_event_schedule_expression
}

module "lr_27" {
  source = "./LR_27_job_cleanup"

  lambda_name                           = local.lambda_name.lr_27
  package_layer_arn                     = aws_lambda_layer_version.package_layer.arn
  runtime                               = var.runtime
  suffix                                = var.suffix
  cloudwatch_kms_key                    = var.cloudwatch_kms_key
  dynamodb_kms_key                      = var.dynamodb_kms_key
  s3_kms_key                            = var.s3_kms_key
  log_retention_in_days                 = var.log_retention_in_days
  lr_13_registrations_output_bucket     = var.s3_buckets.LR-13.bucket
  lr_13_registrations_output_bucket_arn = var.s3_buckets.LR-13.arn
  jobs_table_arn                        = var.dynamodb_tables.jobs.arn
  jobs_table_name                       = var.dynamodb_tables.jobs.name
  in_flight_table_arn                   = var.dynamodb_tables.in_flight.arn
  in_flight_table_name                  = var.dynamodb_tables.in_flight.name
}
