module "lr_01_gp_extract_input" {
  source = "../../modules/s3_bucket"

  name                    = "lr-01-gp-extract-input"
  environment             = local.environment
  s3_force_destroy_bucket = try(local.s3_force_destroy_bucket[local.environment], local.s3_force_destroy_bucket["default"])
  s3_logging_bucket_name  = module.lr_26_access_logs.bucket.bucket
  s3_logging_kms_arn      = module.kms["s3"].key.arn
  log_retention_in_days   = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])

  s3_triggers = [
    {
      events              = ["s3:ObjectCreated:*"]
      lambda_function_arn = module.lr_02_validate_and_parse.lambda.arn
      key_prefix          = "inbound/"
    },
    {
      events              = ["s3:ObjectCreated:*"]
      lambda_function_arn = module.lr_04_feedback_failure.lambda.arn
      key_prefix          = "fail/"
    }
  ]
}

#tfsec:ignore:aws-s3-enable-versioning
module "lr_06_patient_records" {
  source = "../../modules/s3_bucket"

  name                    = "lr-06-patient-records"
  environment             = local.environment
  s3_force_destroy_bucket = try(local.s3_force_destroy_bucket[local.environment], local.s3_force_destroy_bucket["default"])
  s3_logging_bucket_name  = module.lr_26_access_logs.bucket.bucket
  s3_logging_kms_arn      = module.kms["s3"].key.arn
  log_retention_in_days   = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  versioning_enabled      = false

  s3_triggers = [{
    events              = ["s3:ObjectCreated:*"]
    lambda_function_arn = module.lr_07_pds_hydrate.lambda.arn
    key_prefix          = null
  }]
}

module "lr_13_reg_diffs_output" {
  source = "../../modules/s3_bucket"

  name                    = "lr-13-reg-diffs-output"
  environment             = local.environment
  s3_force_destroy_bucket = try(local.s3_force_destroy_bucket[local.environment], local.s3_force_destroy_bucket["default"])
  s3_logging_bucket_name  = module.lr_26_access_logs.bucket.bucket
  s3_logging_kms_arn      = module.kms["s3"].key.arn
  log_retention_in_days   = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
}

#tfsec:ignore:aws-s3-enable-versioning
module "lr_20_pds_reg_input" {
  source = "../../modules/s3_bucket"

  name                    = "lr-20-pds-reg-input"
  environment             = local.environment
  s3_force_destroy_bucket = try(local.s3_force_destroy_bucket[local.environment], local.s3_force_destroy_bucket["default"])
  s3_logging_bucket_name  = module.lr_26_access_logs.bucket.bucket
  s3_logging_kms_arn      = module.kms["s3"].key.arn
  log_retention_in_days   = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  versioning_enabled      = false

  s3_triggers = [
    {
      events              = ["s3:ObjectCreated:*"],
      lambda_function_arn = module.lr_21_split_dps_extract.lambda.arn
      key_prefix          = null
    }
  ]
}

#tfsec:ignore:aws-s3-enable-versioning
module "lr_22_pds_reg_output" {
  source = "../../modules/s3_bucket"

  name                    = "lr-22-pds-reg-output"
  environment             = local.environment
  s3_force_destroy_bucket = try(local.s3_force_destroy_bucket[local.environment], local.s3_force_destroy_bucket["default"])
  s3_logging_bucket_name  = module.lr_26_access_logs.bucket.bucket
  s3_logging_kms_arn      = module.kms["s3"].key.arn
  log_retention_in_days   = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  versioning_enabled      = false
}

#tfsec:ignore:aws-s3-enable-bucket-logging tfsec:ignore:custom-custom-lr-all-buckets-log tfsec:ignore:aws-s3-enable-versioning
module "lr_23_firehose_failure" {
  source = "../../modules/s3_bucket"

  name                    = "lr-23-firehose-failure"
  environment             = local.environment
  s3_force_destroy_bucket = try(local.s3_force_destroy_bucket[local.environment], local.s3_force_destroy_bucket["default"])
  s3_logging_enabled      = false
  s3_logging_bucket_name  = "N/A"
  s3_logging_kms_arn      = module.kms["s3"].key.arn
  log_retention_in_days   = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  versioning_enabled      = false
}

#tfsec:ignore:aws-s3-enable-bucket-logging tfsec:ignore:custom-custom-lr-all-buckets-log tfsec:ignore:aws-s3-enable-versioning
module "lr_26_access_logs" {
  source = "../../modules/s3_bucket"

  name                    = "lr-26-access-logs"
  environment             = local.environment
  s3_acl                  = "log-delivery-write"
  s3_force_destroy_bucket = try(local.s3_force_destroy_bucket[local.environment], local.s3_force_destroy_bucket["default"])
  s3_logging_enabled      = false
  s3_logging_bucket_name  = "N/A"
  s3_logging_kms_arn      = module.kms["s3"].key.arn
  log_retention_in_days   = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  versioning_enabled      = false
}

#tfsec:ignore:aws-s3-enable-versioning
module "mesh_bucket" {
  source = "../../modules/s3_bucket"

  name                    = "mesh-bucket"
  environment             = local.environment
  s3_force_destroy_bucket = try(local.s3_force_destroy_bucket[local.environment], local.s3_force_destroy_bucket["default"])
  s3_logging_bucket_name  = module.lr_26_access_logs.bucket.bucket
  s3_logging_kms_arn      = module.kms["s3"].key.arn
  log_retention_in_days   = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  versioning_enabled      = false
}
