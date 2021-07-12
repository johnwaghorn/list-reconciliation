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

#---------------------Lambda Package layer ----------------
data "archive_file" "packages" {
  type        = "zip"
  source_dir  = "${path.module}/../../../lambda_layer"
  output_path = "${path.module}/../../../lambda_layer.zip"
}

resource "aws_lambda_layer_version" "package_layer" {
  filename            = data.archive_file.packages.output_path
  layer_name          = "lambda_layer_${var.suffix}"
  compatible_runtimes = ["python3.8"]
  source_code_hash    = data.archive_file.packages.output_base64sha256
}

# -----------------------Lambdas ----------------------
module "LR-02" {
  source                  = "../lambdas/LR-02"
  lambda_name             = local.lambda_name.LR-02
  package_layer_arn       = aws_lambda_layer_version.package_layer.arn
  runtime                 = var.runtime
  source_bucket           = aws_s3_bucket.LR-01.bucket
  lr_01_inbound_folder    = aws_s3_bucket_object.inbound.key
  patient_sqs_arn         = aws_sqs_queue.Patient_Records_Queue.arn
  patient_sqs_name        = aws_sqs_queue.Patient_Records_Queue.name
  demographics_table_arn  = var.dynamodb_tables.demographics.arn
  demographics_table_name = var.dynamodb_tables.demographics.name
  errors_table_arn        = var.dynamodb_tables.errors.arn
  errors_table_name       = var.dynamodb_tables.errors.name
  inflight_table_arn      = var.dynamodb_tables.inflight.arn
  inflight_table_name     = var.dynamodb_tables.inflight.name
  jobs_table_arn          = var.dynamodb_tables.jobs.arn
  jobs_table_name         = var.dynamodb_tables.jobs.name
  suffix                  = var.suffix
  lambda_handler          = var.lambda_handler
}

module "LR-07" {
  source                   = "../lambdas/LR-07"
  lambda_name              = local.lambda_name.LR-07
  package_layer_arn        = aws_lambda_layer_version.package_layer.arn
  runtime                  = var.runtime
  lambda_timeout           = var.lambda_timeout
  lr_08_lambda             = module.LR-08.LR-08-lambda_arn
  patient_sqs_arn          = aws_sqs_queue.Patient_Records_Queue.arn
  demographics_table_arn   = var.dynamodb_tables.demographics.arn
  demographics_table_name  = var.dynamodb_tables.demographics.name
  errors_table_arn         = var.dynamodb_tables.errors.arn
  errors_table_name        = var.dynamodb_tables.errors.name
  mock_pds_data_bucket_arn = aws_s3_bucket.mock-pds-data.arn
  pds_url                  = "s3://${aws_s3_bucket.mock-pds-data.bucket}/${var.pds_url}"
  suffix                   = var.suffix
  lambda_handler           = var.lambda_handler
}

module "LR-08" {
  source                              = "../lambdas/LR-08"
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
}

module "LR-09" {
  source                  = "../lambdas/LR-09"
  lambda_name             = local.lambda_name.LR-09
  runtime                 = var.runtime
  lambda_timeout          = var.lambda_timeout
  package_layer_arn       = aws_lambda_layer_version.package_layer.arn
  lr_10_step_function_arn = module.LR-10.LR-10-step_function_arn
  demographics_table_arn  = var.dynamodb_tables.demographics.arn
  demographics_table_name = var.dynamodb_tables.demographics.name
  jobs_table_arn          = var.dynamodb_tables.jobs.arn
  jobs_table_name         = var.dynamodb_tables.jobs.name
  job_stats_table_arn     = var.dynamodb_tables.jobs_stats.arn
  job_stats_table_name    = var.dynamodb_tables.jobs_stats.name
  inflight_table_arn      = var.dynamodb_tables.inflight.arn
  inflight_table_name     = var.dynamodb_tables.inflight.name
  errors_table_arn        = var.dynamodb_tables.errors.arn
  errors_table_name       = var.dynamodb_tables.errors.name
  suffix                  = var.suffix
  lambda_handler          = var.lambda_handler
}

module "LR-11" {
  source                          = "../lambdas/LR-11"
  lambda_name                     = local.lambda_name.LR-11
  runtime                         = var.runtime
  lambda_timeout                  = var.lambda_timeout
  package_layer_arn               = aws_lambda_layer_version.package_layer.arn
  registrations_output_bucket_arn = aws_s3_bucket.LR-13.arn
  registrations_output_bucket     = aws_s3_bucket.LR-13.bucket
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
}

module "LR-12" {
  source                                = "../lambdas/LR-12"
  lambda_name                           = local.lambda_name.LR-12
  runtime                               = var.runtime
  lambda_timeout                        = var.lambda_timeout
  package_layer_arn                     = aws_lambda_layer_version.package_layer.arn
  registrations_output_bucket_arn       = aws_s3_bucket.LR-13.arn
  registrations_output_bucket           = aws_s3_bucket.LR-13.bucket
  pds_practice_registrations_bucket_arn = aws_s3_bucket.LR-22.arn
  pds_practice_registrations_bucket     = aws_s3_bucket.LR-22.bucket
  demographics_table_arn                = var.dynamodb_tables.demographics.arn
  demographics_table_name               = var.dynamodb_tables.demographics.name
  jobs_table_arn                        = var.dynamodb_tables.jobs.arn
  jobs_table_name                       = var.dynamodb_tables.jobs.name
  job_stats_table_arn                   = var.dynamodb_tables.jobs_stats.arn
  job_stats_table_name                  = var.dynamodb_tables.jobs_stats.name
  errors_table_arn                      = var.dynamodb_tables.errors.arn
  errors_table_name                     = var.dynamodb_tables.errors.name
  mock_pds_data_bucket_arn              = aws_s3_bucket.mock-pds-data.arn
  pds_url                               = "s3://${aws_s3_bucket.mock-pds-data.bucket}/${var.pds_url}"
  pds_api_retries                       = var.pds_api_retries
  suffix                                = var.suffix
  lambda_handler                        = var.lambda_handler
}

module "LR-15" {
  source                              = "../lambdas/LR-15"
  lambda_name                         = local.lambda_name.LR-15
  runtime                             = var.runtime
  lambda_timeout                      = var.lambda_timeout
  package_layer_arn                   = aws_lambda_layer_version.package_layer.arn
  mesh_send_bucket_arn                = aws_s3_bucket.LR-23.arn
  mesh_send_bucket                    = aws_s3_bucket.LR-23.bucket
  registrations_output_bucket_arn     = aws_s3_bucket.LR-13.arn
  registrations_output_bucket         = aws_s3_bucket.LR-13.bucket
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
}

module "LR-21" {
  source                      = "../lambdas/LR-21"
  lambda_name                 = local.lambda_name.LR-21
  runtime                     = var.runtime
  package_layer_arn           = aws_lambda_layer_version.package_layer.arn
  supplementary-input-bucket  = aws_s3_bucket.LR-20.bucket
  supplementary-output-bucket = aws_s3_bucket.LR-22.bucket
  errors_table_arn            = var.dynamodb_tables.errors.arn
  errors_table_name           = var.dynamodb_tables.errors.name
  suffix                      = var.suffix
  lambda_handler              = var.lambda_handler
}

# -----------------------Step functions ----------------------
module "LR-10" {
  source       = "../step_functions/LR-10"
  name         = "LR_10_registration-differences-${var.suffix}"
  lr_11_lambda = module.LR-11.LR_11_lambda_arn
  lr_12_lambda = module.LR-12.LR-12-lambda_arn
  lr_15_lambda = module.LR-15.LR-15-lambda_arn
}
