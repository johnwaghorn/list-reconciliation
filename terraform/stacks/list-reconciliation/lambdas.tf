module "packages" {
  source = "../../modules/lambda_layer"

  name       = "packages_layer_${local.environment}"
  source_dir = "packages_layer"
}

module "dependencies" {
  source = "../../modules/lambda_layer"

  name       = "dependencies_layer_${local.environment}"
  source_dir = "dependencies_layer"
}

module "lr_02_validate_and_parse" {
  source = "../../modules/lambda_function"

  name                   = "lr_02_validate_and_parse"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.intra_subnets

  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 4
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
    { id = module.lambda_endpoint.security_group.id, port = 443 },
  ]

  dynamodb_read_write   = [module.lr_29_in_flight.table.arn, module.lr_03_jobs.table.arn]
  kms_read_write        = [module.kms["dynamodb"].key.arn, module.kms["s3"].key.arn]
  lambda_layers         = [module.packages.layer.arn, module.dependencies.layer.arn]
  lambdas_to_invoke     = [module.lr_24_save_records_to_s3.lambda.arn]
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  s3_read_write         = [module.lr_01_gp_extract_input.bucket.arn]
  ssm_read_only         = [module.list_rec_email_password.parameter.arn]
  environment_variables = {
    AWS_S3_REGISTRATION_EXTRACT_BUCKET = module.lr_01_gp_extract_input.bucket.bucket
    INFLIGHT_TABLE                     = module.lr_29_in_flight.table.name
    JOBS_TABLE                         = module.lr_03_jobs.table.name
    LR_06_BUCKET                       = module.lr_06_patient_records.bucket.bucket
    LR_24_SAVE_RECORDS_TO_S3           = module.lr_24_save_records_to_s3.lambda.arn
  }
}

#tfsec:ignore:aws-vpc-no-public-egress-sgr
module "lr_04_feedback_failure" {
  source = "../../modules/lambda_function"

  name                   = "lr_04_feedback_failure"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.private_subnets

  cidr_block_egresses_length = 1
  cidr_block_egresses = [
    { cidr_block = "0.0.0.0/0", port = 443 }
  ]
  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 3
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
  ]

  kms_read_write        = [module.kms["ssm"].key.arn, module.kms["s3"].key.arn]
  lambda_layers         = [module.packages.layer.arn, module.dependencies.layer.arn]
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  s3_read_write         = [module.lr_01_gp_extract_input.bucket.arn]
  ssm_read_by_path      = ["arn:aws:ssm:eu-west-2:${data.aws_caller_identity.current.account_id}:parameter/${local.environment}/email/*"]
  environment_variables = {
    AWS_S3_REGISTRATION_EXTRACT_BUCKET = module.lr_01_gp_extract_input.bucket.bucket
    EMAIL_SSM_PREFIX                   = "/${local.environment}/email/"
    LISTREC_EMAIL                      = try(local.listrec_email[local.environment], local.listrec_email["default"])
    PCSE_EMAIL                         = try(local.pcse_email[local.environment], local.pcse_email["default"])
  }
}

#tfsec:ignore:aws-vpc-no-public-egress-sgr
module "lr_07_pds_hydrate" {
  source = "../../modules/lambda_function"

  name                   = "lr_07_pds_hydrate"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.private_subnets

  cidr_block_egresses_length = 1
  cidr_block_egresses = [
    { cidr_block = "0.0.0.0/0", port = 443 }
  ]
  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 4
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
    { id = module.lambda_endpoint.security_group.id, port = 443 },
  ]

  dynamodb_read_write            = [module.lr_30_demographics.table.arn]
  kms_read_write                 = [module.kms["dynamodb"].key.arn, module.kms["ssm"].key.arn, module.kms["s3"].key.arn]
  lambda_layers                  = [module.packages.layer.arn, module.dependencies.layer.arn]
  lambdas_to_invoke              = [module.lr_08_demographic_comparison.lambda.arn]
  log_retention_in_days          = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  reserved_concurrent_executions = try(local.lr_07_reserved_concurrent_executions[local.environment], local.lr_07_reserved_concurrent_executions["default"])
  s3_read_write                  = [module.lr_06_patient_records.bucket.arn]
  ssm_read_write                 = [module.pds_api_access_token.parameter.arn]
  ssm_read_by_path               = ["arn:aws:ssm:eu-west-2:${data.aws_caller_identity.current.account_id}:parameter/${local.environment}/pds/*"]
  environment_variables = {
    DEMOGRAPHIC_COMPARISON_LAMBDA = module.lr_08_demographic_comparison.lambda.arn
    DEMOGRAPHICS_TABLE            = module.lr_30_demographics.table.name
    PDS_BASE_URL                  = try(local.pds_fhir_api_url[local.environment], local.pds_fhir_api_url["default"])
    SSM_STORE_PREFIX              = "/${local.environment}/pds/"
  }
}

module "lr_08_demographic_comparison" {
  source = "../../modules/lambda_function"

  name                   = "lr_08_demographic_comparison"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.intra_subnets

  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 3
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
  ]

  dynamodb_read_write   = [module.lr_30_demographics.table.arn, module.lr_31_demographics_differences.table.arn]
  kms_read_write        = [module.kms["dynamodb"].key.arn, module.kms["s3"].key.arn]
  lambda_layers         = [module.packages.layer.arn, module.dependencies.layer.arn]
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])

  environment_variables = {
    DEMOGRAPHICS_DIFFERENCES_TABLE = module.lr_31_demographics_differences.table.name
    DEMOGRAPHICS_TABLE             = module.lr_30_demographics.table.name
  }
}

module "lr_09_scheduled_check" {
  source = "../../modules/lambda_function"

  name                   = "lr_09_scheduled_check"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.intra_subnets

  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 4
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
    { id = module.step_function_endpoint.security_group.id, port = 443 },
  ]

  dynamodb_read_write = [
    module.lr_30_demographics.table.arn, "${module.lr_30_demographics.table.arn}/index/*",
    module.lr_03_jobs.table.arn, "${module.lr_03_jobs.table.arn}/index/*",
    module.lr_28_jobs_stats.table.arn,
    module.lr_29_in_flight.table.arn
  ]
  event_schedule_expression = try(local.lr_09_event_schedule_expression[local.environment], local.lr_09_event_schedule_expression["default"])
  kms_read_write            = [module.kms["dynamodb"].key.arn, module.kms["s3"].key.arn]
  lambda_layers             = [module.packages.layer.arn, module.dependencies.layer.arn]
  log_retention_in_days     = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  step_functions_to_invoke  = [module.lr_10_registration_orchestration.step_function.arn]
  environment_variables = {
    DEMOGRAPHICS_TABLE      = module.lr_30_demographics.table.name
    INFLIGHT_TABLE          = module.lr_29_in_flight.table.name
    JOB_STATS_TABLE         = module.lr_28_jobs_stats.table.name
    JOB_TIMEOUT_HOURS       = try(local.lr_09_job_timeout_hours[local.environment], local.lr_09_job_timeout_hours["default"])
    JOBS_TABLE              = module.lr_03_jobs.table.name
    LR_10_STEP_FUNCTION_ARN = module.lr_10_registration_orchestration.step_function.arn
  }
}

module "lr_11_gp_registration_status" {
  source = "../../modules/lambda_function"

  name                   = "lr_11_gp_registration_status"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.intra_subnets

  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 3
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
  ]

  dynamodb_read_write = [
    module.lr_30_demographics.table.arn, "${module.lr_30_demographics.table.arn}/index/*",
    module.lr_03_jobs.table.arn, "${module.lr_03_jobs.table.arn}/index/*",
    module.lr_28_jobs_stats.table.arn
  ]
  kms_read_write        = [module.kms["dynamodb"].key.arn, module.kms["s3"].key.arn]
  lambda_layers         = [module.packages.layer.arn, module.dependencies.layer.arn]
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  s3_read_write         = [module.lr_13_reg_diffs_output.bucket.arn]
  environment_variables = {
    DEMOGRAPHICS_TABLE                = module.lr_30_demographics.table.name
    JOB_STATS_TABLE                   = module.lr_28_jobs_stats.table.name
    JOBS_TABLE                        = module.lr_03_jobs.table.name
    LR_13_REGISTRATIONS_OUTPUT_BUCKET = module.lr_13_reg_diffs_output.bucket.bucket
  }
}

#tfsec:ignore:aws-vpc-no-public-egress-sgr
module "lr_12_pds_registration_status" {
  source = "../../modules/lambda_function"

  name                   = "lr_12_pds_registration_status"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.private_subnets

  cidr_block_egresses_length = 1
  cidr_block_egresses = [
    { cidr_block = "0.0.0.0/0", port = 443 }
  ]
  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 3
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
  ]

  dynamodb_read_write = [
    module.lr_30_demographics.table.arn, "${module.lr_30_demographics.table.arn}/index/*",
    module.lr_03_jobs.table.arn,
    module.lr_28_jobs_stats.table.arn
  ]
  kms_read_write        = [module.kms["dynamodb"].key.arn, module.kms["ssm"].key.arn, module.kms["s3"].key.arn]
  lambda_layers         = [module.packages.layer.arn, module.dependencies.layer.arn]
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  s3_read_write         = [module.lr_13_reg_diffs_output.bucket.arn, module.lr_22_pds_reg_output.bucket.arn]
  ssm_read_by_path      = ["arn:aws:ssm:eu-west-2:${data.aws_caller_identity.current.account_id}:parameter/${local.environment}/pds/*"]
  ssm_read_write        = [module.pds_api_access_token.parameter.arn]
  environment_variables = {
    DEMOGRAPHICS_TABLE                      = module.lr_30_demographics.table.name
    JOB_STATS_TABLE                         = module.lr_28_jobs_stats.table.name
    JOBS_TABLE                              = module.lr_03_jobs.table.name
    LR_13_REGISTRATIONS_OUTPUT_BUCKET       = module.lr_13_reg_diffs_output.bucket.bucket
    LR_22_PDS_PRACTICE_REGISTRATIONS_BUCKET = module.lr_22_pds_reg_output.bucket.bucket
    PDS_API_RETRIES                         = 3
    PDS_BASE_URL                            = try(local.pds_fhir_api_url[local.environment], local.pds_fhir_api_url["default"])
    SSM_STORE_PREFIX                        = "/${local.environment}/pds/"
  }
}

#tfsec:ignore:aws-vpc-no-public-egress-sgr
module "lr_14_send_list_rec_results" {
  source = "../../modules/lambda_function"

  name                   = "lr_14_send_list_rec_results"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.private_subnets

  cidr_block_egresses_length = 1
  cidr_block_egresses = [
    { cidr_block = "0.0.0.0/0", port = 443 }
  ]
  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 3
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
  ]

  dynamodb_read_write = [
    module.lr_31_demographics_differences.table.arn, "${module.lr_31_demographics_differences.table.arn}/index/*",
    module.lr_03_jobs.table.arn, "${module.lr_03_jobs.table.arn}/index/*",
    module.lr_28_jobs_stats.table.arn
  ]
  kms_read_write        = [module.kms["dynamodb"].key.arn, module.kms["mesh"].key.arn, module.kms["ssm"].key.arn, module.kms["s3"].key.arn]
  lambda_layers         = [module.packages.layer.arn, module.dependencies.layer.arn]
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  ssm_read_by_path = [
    "arn:aws:ssm:eu-west-2:${data.aws_caller_identity.current.account_id}:parameter/${local.environment}/email/*",
    "arn:aws:ssm:eu-west-2:${data.aws_caller_identity.current.account_id}:parameter/${local.environment}/mesh/*"
  ]
  s3_read_write = [module.lr_13_reg_diffs_output.bucket.arn, module.mesh_bucket.bucket.arn]
  environment_variables = {
    DEMOGRAPHICS_DIFFERENCES_TABLE    = module.lr_31_demographics_differences.table.name
    EMAIL_SSM_PREFIX                  = "/${local.environment}/email/"
    JOB_STATS_TABLE                   = module.lr_28_jobs_stats.table.name
    JOBS_TABLE                        = module.lr_03_jobs.table.name
    LISTREC_EMAIL                     = try(local.listrec_email[local.environment], local.listrec_email["default"])
    LR_13_REGISTRATIONS_OUTPUT_BUCKET = module.lr_13_reg_diffs_output.bucket.bucket
    MESH_BUCKET                       = module.mesh_bucket.bucket.bucket
    MESH_SSM_PREFIX                   = "/${local.environment}/mesh/"
    PCSE_EMAIL                        = try(local.pcse_email[local.environment], local.pcse_email["default"])
    SEND_EMAILS                       = try(local.send_emails[local.environment], local.send_emails["default"])
  }
}

module "lr_15_process_demo_diffs" {
  source = "../../modules/lambda_function"

  name                   = "lr_15_process_demo_diffs"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.intra_subnets

  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 3
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
  ]

  dynamodb_read_write = [
    module.lr_30_demographics.table.arn, "${module.lr_30_demographics.table.arn}/index/*",
    module.lr_31_demographics_differences.table.arn, "${module.lr_31_demographics_differences.table.arn}/index/*",
    module.lr_03_jobs.table.arn,
    module.lr_28_jobs_stats.table.arn
  ]
  kms_read_write        = [module.kms["dynamodb"].key.arn, module.kms["mesh"].key.arn, module.kms["ssm"].key.arn, module.kms["s3"].key.arn]
  lambda_layers         = [module.packages.layer.arn, module.dependencies.layer.arn]
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  s3_read_write         = [module.lr_13_reg_diffs_output.bucket.arn, module.mesh_bucket.bucket.arn]
  ssm_read_by_path      = ["arn:aws:ssm:eu-west-2:${data.aws_caller_identity.current.account_id}:parameter/${local.environment}/mesh/*"]
  environment_variables = {
    DEMOGRAPHICS_DIFFERENCES_TABLE    = module.lr_31_demographics_differences.table.name
    DEMOGRAPHICS_TABLE                = module.lr_30_demographics.table.name
    JOB_STATS_TABLE                   = module.lr_28_jobs_stats.table.name
    JOBS_TABLE                        = module.lr_03_jobs.table.name
    LR_13_REGISTRATIONS_OUTPUT_BUCKET = module.lr_13_reg_diffs_output.bucket.bucket
    MESH_BUCKET                       = module.mesh_bucket.bucket.bucket
    MESH_SSM_PREFIX                   = "/${local.environment}/mesh/"
  }
}

module "lr_21_split_dps_extract" {
  source = "../../modules/lambda_function"

  name                   = "lr_21_split_dps_extract"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.intra_subnets

  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 4
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
    { id = module.lambda_endpoint.security_group.id, port = 443 },
  ]

  kms_read_write        = [module.kms["s3"].key.arn]
  lambda_invoke_self    = true
  lambda_layers         = [module.packages.layer.arn, module.dependencies.layer.arn]
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  s3_read_only          = [module.lr_20_pds_reg_input.bucket.arn]
  s3_read_write         = [module.lr_22_pds_reg_output.bucket.arn]
  environment_variables = {
    LR_20_SUPPLEMENTARY_INPUT_BUCKET  = module.lr_20_pds_reg_input.bucket.bucket
    LR_22_SUPPLEMENTARY_OUTPUT_BUCKET = module.lr_22_pds_reg_output.bucket.bucket
  }
}

module "lr_24_save_records_to_s3" {
  source = "../../modules/lambda_function"

  name                   = "lr_24_save_records_to_s3"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.intra_subnets

  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 3
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
  ]

  kms_read_write        = [module.kms["s3"].key.arn]
  lambda_layers         = [module.packages.layer.arn, module.dependencies.layer.arn]
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  s3_read_write         = [module.lr_06_patient_records.bucket.arn]
}

module "lr_25_mesh_post_office" {
  source = "../../modules/lambda_function"

  name                   = "lr_25_mesh_post_office"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.intra_subnets

  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 3
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
  ]

  event_schedule_expression = try(local.lr_25_event_schedule_expression[local.environment], local.lr_25_event_schedule_expression["default"])
  kms_read_write            = [module.kms["mesh"].key.arn, module.kms["s3"].key.arn]
  lambda_layers             = [module.packages.layer.arn, module.dependencies.layer.arn]
  log_retention_in_days     = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  ssm_read_by_path          = ["arn:aws:ssm:eu-west-2:${data.aws_caller_identity.current.account_id}:parameter/${local.environment}/lr_25_mesh_post_office/*"]
}

module "lr_27_job_cleanup" {
  source = "../../modules/lambda_function"

  name                   = "lr_27_job_cleanup"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.intra_subnets

  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 3
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
  ]

  dynamodb_read_write   = [module.lr_03_jobs.table.arn, module.lr_29_in_flight.table.arn]
  kms_read_write        = [module.kms["dynamodb"].key.arn, module.kms["s3"].key.arn]
  lambda_layers         = [module.packages.layer.arn, module.dependencies.layer.arn]
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
  s3_read_write         = [module.lr_13_reg_diffs_output.bucket.arn]
  environment_variables = {
    INFLIGHT_TABLE                    = module.lr_29_in_flight.table.name
    JOBS_TABLE                        = module.lr_03_jobs.table.name
    LR_13_REGISTRATIONS_OUTPUT_BUCKET = module.lr_13_reg_diffs_output.bucket.bucket
  }
}

module "lr_29_firehose_transform" {
  source = "../../modules/lambda_function"

  name                   = "lr_29_firehose_transform"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.intra_subnets

  prefix_list_egresses_length = 2
  prefix_list_egresses = [
    { id = module.s3_endpoint.endpoint.prefix_list_id, port = 443 },
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 3
  security_group_egresses = [
    { id = module.cloudwatch_endpoint.security_group.id, port = 443 },
    { id = module.kms_endpoint.security_group.id, port = 443 },
    { id = module.ssm_endpoint.security_group.id, port = 443 },
  ]

  lambda_layers         = [module.packages.layer.arn]
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])

  environment_variables = {
    SPLUNK_SOURCETYPE = "pcrm-listrecon:aws:cloudwatch_logs"
  }
}
