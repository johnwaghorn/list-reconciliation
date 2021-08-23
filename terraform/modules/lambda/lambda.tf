locals {
  lambda_name = {
    lr_02 = "lr_02_validate_and_parse"
    lr_04 = "lr_04_feedback_failure"
    lr_07 = "lr_07_pds_hydrate"
    lr_08 = "lr_08_demographic_comparison"
    lr_09 = "lr_09_scheduled_check"
    lr_11 = "lr_11_gp_registration_status"
    lr_12 = "lr_12_pds_registration_status"
    lr_14 = "lr_14_send_list_rec_results"
    lr_15 = "lr_15_process_demo_diffs"
    lr_21 = "lr_21_split_dps_extract"
    lr_24 = "lr_24_save_records_to_s3"
    lr_25 = "lr_25_mesh_post_office"
    lr_27 = "lr_27_job_cleanup"
  }
}

module "lr_02_validate_and_parse" {
  source = "./lr_02_validate_and_parse"

  lambda_name           = local.lambda_name.lr_02
  lambda_layers         = [aws_lambda_layer_version.packages_layer.arn, aws_lambda_layer_version.dependencies_layer.arn]
  source_bucket         = var.s3_buckets.LR-01.bucket
  source_bucket_arn     = var.s3_buckets.LR-01.arn
  lr_01_inbound_folder  = var.s3_buckets.LR-01.inbound_key
  lr_01_failed_folder   = var.s3_buckets.LR-01.fail_key
  lr_06_bucket          = var.s3_buckets.LR-06.bucket
  lr_04_lambda_arn      = module.lr_04_feedback_failure.LR-04-lambda_arn
  lr_24_lambda_arn      = module.lr_24_save_records_to_s3.LR-24-lambda_arn
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

module "lr_04_feedback_failure" {
  source = "./lr_04_feedback_failure"

  lambda_name           = local.lambda_name.lr_04
  lambda_layers         = [aws_lambda_layer_version.packages_layer.arn, aws_lambda_layer_version.dependencies_layer.arn]
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

module "lr_07_pds_hydrate" {
  source = "./lr_07_pds_hydrate"

  lambda_name                          = local.lambda_name.lr_07
  lambda_layers                        = [aws_lambda_layer_version.packages_layer.arn, aws_lambda_layer_version.dependencies_layer.arn]
  lambda_timeout                       = var.lambda_timeout
  lr_08_lambda                         = module.lr_08_demographic_comparison.LR-08-lambda_arn
  demographics_table_arn               = var.dynamodb_tables.demographics.arn
  demographics_table_name              = var.dynamodb_tables.demographics.name
  lr_06_bucket_arn                     = var.s3_buckets.LR-06.arn
  lr_06_bucket                         = var.s3_buckets.LR-06.bucket
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

module "lr_08_demographic_comparison" {
  source = "./lr_08_demographic_comparison"

  lambda_name                         = local.lambda_name.lr_08
  lambda_timeout                      = var.lambda_timeout
  lambda_layers                       = [aws_lambda_layer_version.packages_layer.arn, aws_lambda_layer_version.dependencies_layer.arn]
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

module "lr_09_scheduled_check" {
  source = "./lr_09_scheduled_check"

  lambda_name                     = local.lambda_name.lr_09
  lambda_timeout                  = var.lambda_timeout
  lambda_layers                   = [aws_lambda_layer_version.packages_layer.arn, aws_lambda_layer_version.dependencies_layer.arn]
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

module "lr_11_gp_registration_status" {
  source = "./lr_11_gp_registration_status"

  lambda_name                     = local.lambda_name.lr_11
  lambda_timeout                  = var.lambda_timeout
  lambda_layers                   = [aws_lambda_layer_version.packages_layer.arn, aws_lambda_layer_version.dependencies_layer.arn]
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

module "lr_12_pds_registration_status" {
  source = "./lr_12_pds_registration_status"

  lambda_name                           = local.lambda_name.lr_12
  lambda_timeout                        = var.lambda_timeout
  lambda_layers                         = [aws_lambda_layer_version.packages_layer.arn, aws_lambda_layer_version.dependencies_layer.arn]
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

module "lr_14_send_list_rec_results" {
  source = "./lr_14_send_list_rec_results"

  lambda_name                         = local.lambda_name.lr_14
  lambda_timeout                      = var.lambda_timeout
  lambda_layers                       = [aws_lambda_layer_version.packages_layer.arn, aws_lambda_layer_version.dependencies_layer.arn]
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

module "lr_15_process_demo_diffs" {
  source = "./lr_15_process_demo_diffs"

  lambda_name                         = local.lambda_name.lr_15
  lambda_timeout                      = var.lambda_timeout
  lambda_layers                       = [aws_lambda_layer_version.packages_layer.arn, aws_lambda_layer_version.dependencies_layer.arn]
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

module "lr_21_split_dps_extract" {
  source = "./lr_21_split_dps_extract"

  lambda_name                     = local.lambda_name.lr_21
  lambda_layers                   = [aws_lambda_layer_version.packages_layer.arn, aws_lambda_layer_version.dependencies_layer.arn]
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

module "lr_24_save_records_to_s3" {
  source = "./lr_24_save_records_to_s3"

  lambda_name           = local.lambda_name.lr_24
  lambda_layers         = [aws_lambda_layer_version.packages_layer.arn, aws_lambda_layer_version.dependencies_layer.arn]
  lambda_timeout        = var.lambda_timeout
  suffix                = var.suffix
  lr-06-bucket          = var.s3_buckets.LR-06.bucket
  lr-06-bucket_arn      = var.s3_buckets.LR-06.arn
  lambda_handler        = var.lambda_handler
  cloudwatch_kms_key    = var.cloudwatch_kms_key
  s3_kms_key            = var.s3_kms_key
  log_retention_in_days = var.log_retention_in_days
}

module "lr_25_mesh_post_office" {
  source = "./lr_25_mesh_post_office"

  lambda_name                     = local.lambda_name.lr_25
  lambda_layers                   = [aws_lambda_layer_version.packages_layer.arn, aws_lambda_layer_version.dependencies_layer.arn]
  suffix                          = var.suffix
  mesh_kms_key_alias              = var.mesh_kms_key_alias
  mesh_post_office_open           = var.mesh_post_office_open
  mesh_post_office_mappings       = var.mesh_post_office_mappings
  cloudwatch_kms_key              = var.cloudwatch_kms_key
  s3_kms_key                      = var.s3_kms_key
  log_retention_in_days           = var.log_retention_in_days
  lr_25_event_schedule_expression = var.lr_25_event_schedule_expression
}

module "lr_27_job_cleanup" {
  source = "./lr_27_job_cleanup"

  lambda_name                           = local.lambda_name.lr_27
  lambda_layers                         = [aws_lambda_layer_version.packages_layer.arn, aws_lambda_layer_version.dependencies_layer.arn]
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
