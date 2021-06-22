locals {
  lambda_name = {
    LR-02 = "LR_02_validate_and_parse"
    LR-07 = "LR_07_pds_hydrate"
    LR-08 = "LR_08_demographic_comparison"
    LR-09 = "LR_09_scheduled_check"
    LR-11 = "LR_11_gp_registration_status"
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
  layer_name          = "lambda_layer_${terraform.workspace}"
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
  demographics_table_arn  = module.Demographics_Table.dynamo_table_arn
  demographics_table_name = module.Demographics_Table.dynamo_table_name
  errors_table_arn        = module.Errors_Table.dynamo_table_arn
  errors_table_name       = module.Errors_Table.dynamo_table_name
  inflight_table_arn      = module.In_Flight_Table.dynamo_table_arn
  inflight_table_name     = module.In_Flight_Table.dynamo_table_name
  jobs_table_arn          = module.Jobs_Table.dynamo_table_arn
  jobs_table_name         = module.Jobs_Table.dynamo_table_name
}

module "LR-07" {
  source                  = "../lambdas/LR-07"
  lambda_name             = local.lambda_name.LR-07
  package_layer_arn       = aws_lambda_layer_version.package_layer.arn
  runtime                 = var.runtime
  lambda_timeout          = var.lambda_timeout
  lr_08_lambda            = module.LR-08.LR-08-lambda
  patient_sqs_arn         = aws_sqs_queue.Patient_Records_Queue.arn
  demographics_table_arn  = module.Demographics_Table.dynamo_table_arn
  demographics_table_name = module.Demographics_Table.dynamo_table_name
  errors_table_arn        = module.Errors_Table.dynamo_table_arn
  errors_table_name       = module.Errors_Table.dynamo_table_name
}

module "LR-08" {
  source                              = "../lambdas/LR-08"
  lambda_name                         = local.lambda_name.LR-08
  runtime                             = var.runtime
  lambda_timeout                      = var.lambda_timeout
  package_layer_arn                   = aws_lambda_layer_version.package_layer.arn
  demographics_table_arn              = module.Demographics_Table.dynamo_table_arn
  demographics_table_name             = module.Demographics_Table.dynamo_table_name
  errors_table_arn                    = module.Errors_Table.dynamo_table_arn
  errors_table_name                   = module.Errors_Table.dynamo_table_name
  demographics_differences_table_name = module.Demographics_Differences_Table.dynamo_table_name
  demographics_differences_table_arn  = module.Demographics_Differences_Table.dynamo_table_arn
}

module "LR-09" {
  source                  = "../lambdas/LR-09"
  lambda_name             = local.lambda_name.LR-09
  runtime                 = var.runtime
  lambda_timeout          = var.lambda_timeout
  package_layer_arn       = aws_lambda_layer_version.package_layer.arn
  lr_10_step_function_arn = module.LR-10.LR-10-step_function_arn
  demographics_table_arn  = module.Demographics_Table.dynamo_table_arn
  demographics_table_name = module.Demographics_Table.dynamo_table_name
  jobs_table_arn          = module.Jobs_Table.dynamo_table_arn
  jobs_table_name         = module.Jobs_Table.dynamo_table_name
  job_stats_table_arn     = module.Jobs_Stats_Table.dynamo_table_arn
  job_stats_table_name    = module.Jobs_Stats_Table.dynamo_table_name
  inflight_table_arn      = module.In_Flight_Table.dynamo_table_arn
  inflight_table_name     = module.In_Flight_Table.dynamo_table_name
  errors_table_arn        = module.Errors_Table.dynamo_table_arn
  errors_table_name       = module.Errors_Table.dynamo_table_name
}

module "LR-11" {
  source                      = "../lambdas/LR-11"
  lambda_name                 = local.lambda_name.LR-11
  runtime                     = var.runtime
  lambda_timeout              = var.lambda_timeout
  package_layer_arn           = aws_lambda_layer_version.package_layer.arn
  registrations_output_bucket = aws_s3_bucket.LR-13.arn
  demographics_table_arn      = module.Demographics_Table.dynamo_table_arn
  demographics_table_name     = module.Demographics_Table.dynamo_table_name
  jobs_table_arn              = module.Jobs_Table.dynamo_table_arn
  jobs_table_name             = module.Jobs_Table.dynamo_table_name
  job_stats_table_arn         = module.Jobs_Stats_Table.dynamo_table_arn
  job_stats_table_name        = module.Jobs_Stats_Table.dynamo_table_name
  errors_table_arn            = module.Errors_Table.dynamo_table_arn
  errors_table_name           = module.Errors_Table.dynamo_table_name
}

# -----------------------Step functions ----------------------
module "LR-10" {
  source       = "../step_functions/LR-10"
  name         = "LR_10_registration-differences-${terraform.workspace}"
  lr_11_lambda = module.LR-11.LR-11-lambda
}
