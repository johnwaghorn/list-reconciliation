module "lambda" {
  source = "../../modules/lambda"

  suffix                = local.environment
  pds_base_url          = try(local.pds_fhir_api_url[local.environment], local.pds_fhir_api_url["default"])
  pcse_email            = try(local.pcse_email[local.environment], local.pcse_email["default"])
  listrec_email         = "pcrm.gplistreconciliation@nhs.net"
  runtime               = "python3.8"
  lambda_handler        = "main.lambda_handler"
  s3_buckets            = module.s3.buckets
  cloudwatch_kms_key    = module.kms["cloudwatch"].output
  dynamodb_kms_key      = module.kms["dynamodb"].output
  s3_kms_key            = module.kms["s3"].output
  ssm_kms_key           = module.kms["ssm"].output
  pds_ssm_prefix        = module.ssm.pds_ssm_parameters_path
  mesh_ssm_prefix       = module.ssm.mesh_ssm_parameters_path
  email_ssm_prefix      = module.ssm.email_ssm_parameters_path
  pds_ssm_access_token  = module.ssm.pds_ssm_access_token
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  send_emails           = try(local.send_emails[local.environment], local.send_emails["default"])

  lr_07_reserved_concurrent_executions = try(local.lr_07_reserved_concurrent_executions[local.environment], local.lr_07_reserved_concurrent_executions["default"])

  lr_09_event_schedule_expression = try(local.lr_09_event_schedule_expression[local.environment], local.lr_09_event_schedule_expression["default"])
  lr_25_event_schedule_expression = try(local.lr_25_event_schedule_expression[local.environment], local.lr_25_event_schedule_expression["default"])

  mesh_kms_key = local.environment == "prod" ? {
    id  = data.aws_kms_key.mesh_kms[0].id
    arn = data.aws_kms_key.mesh_kms[0].arn
  } : module.kms["mesh"].output

  mesh_kms_key_alias        = try(local.mesh_kms_key_alias[local.environment], local.mesh_kms_key_alias["default"])
  mesh_post_office_open     = try(local.mesh_post_office_open[local.environment], local.mesh_post_office_open["default"])
  mesh_post_office_mappings = try(local.mesh_post_office_mappings[local.environment], local.mesh_post_office_mappings["default"])

  mock_pds_data_bucket = {
    arn  = module.test_data[0].mock_pds_data_bucket_arn
    name = module.test_data[0].mock_pds_data_bucket_name
  }

  step_functions = {
    lr_10_registration_orchestration = {
      arn = module.lr_10_registration_orchestration.arn
    }
  }

  dynamodb_tables = {
    jobs = {
      name = module.jobs.dynamo_table_name
      arn  = module.jobs.dynamo_table_arn
    }
    demographics = {
      name = module.demographics.dynamo_table_name
      arn  = module.demographics.dynamo_table_arn
    }
    in_flight = {
      name = module.in_flight.dynamo_table_name
      arn  = module.in_flight.dynamo_table_arn
    }
    demographics_differences = {
      name = module.demographics_differences.dynamo_table_name
      arn  = module.demographics_differences.dynamo_table_arn
    }
    jobs_stats = {
      name = module.jobs_stats.dynamo_table_name
      arn  = module.jobs_stats.dynamo_table_arn
    }
  }
}

module "s3" {
  source = "../../modules/s3"

  # Allow S3 resources to be destroyed whilst containing data in non-prod envs
  force_destroy         = local.environment == "prod" ? false : true
  suffix                = local.environment
  kms_key_arn           = module.kms["s3"].output.arn
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  mesh_kms_key          = local.environment == "prod" ? data.aws_kms_key.mesh_kms[0].arn : module.kms["mesh"].output.arn
}

module "lr_10_registration_orchestration" {
  source = "../../modules/step_functions/LR-10"

  name         = "LR_10_registration-differences-${local.environment}"
  lr_11_lambda = module.lambda.lr_11_lambda_arn
  lr_12_lambda = module.lambda.lr_12_lambda_arn
  lr_14_lambda = module.lambda.lr_14_lambda_arn
  lr_15_lambda = module.lambda.lr_15_lambda_arn
}

module "kms" {
  for_each = {
    cloudwatch = { name = "cloudwatch-${local.environment}" }
    dynamodb   = { name = "dynamodb-${local.environment}" }
    ssm        = { name = "ssm-${local.environment}" }
    s3         = { name = "s3-${local.environment}" }
    mesh       = { name = "mesh-${local.environment}" }
  }
  source = "../../modules/kms"

  name = each.value.name
}

module "test_data" {
  # only load test data in the non-prod accounts
  count = local.environment != "prod" ? 1 : 0

  source = "../../modules/test_data"

  suffix       = local.environment
  LR_22_bucket = module.s3.buckets.LR-22.bucket
  kms_key_arn  = module.kms["s3"].output.arn
}

module "ssm" {
  source        = "../../modules/ssm"
  prefix        = local.environment
  ssm_kms_arn   = module.kms["ssm"].output.arn
  mesh_mappings = try(local.mesh_mappings[local.environment], local.mesh_mappings["default"])
}
