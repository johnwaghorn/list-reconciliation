module "lambda" {
  source = "../../modules/lambda"

  suffix         = local.environment
  pds_url        = "pds_api_data.csv"
  patient_sqs    = "Patient_Records.fifo"
  runtime        = "python3.8"
  lambda_handler = "main.lambda_handler"
  s3_buckets     = module.s3.buckets

  mock_pds_data_bucket = {
    arn  = module.test_data[0].mock_pds_data_bucket_arn
    name = module.test_data[0].mock_pds_data_bucket_name
  }

  step_functions = {
    lr_10_registration_orchestration = {
      arn = module.lr_10_registration_orchestration.arn
    }
  }

  sqs = {
    patient_records_queue = {
      arn  = module.patient_records_queue.arn
      name = module.patient_records_queue.name
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
    errors = {
      name = module.errors.dynamo_table_name
      arn  = module.errors.dynamo_table_arn
    }
    demographics_differences = {
      name = module.demographics_differences.dynamo_table_name
      arn  = module.demographics_differences.dynamo_table_arn
    }
    jobs_stats = {
      name = module.jobs_stats.dynamo_table_name
      arn  = module.jobs_stats.dynamo_table_arn
    }
    statuses = {
      name = module.statuses.dynamo_table_name
      arn  = module.statuses.dynamo_table_arn
    }
  }
}

module "s3" {
  source = "../../modules/s3"

  suffix = local.environment
}

module "patient_records_queue" {
  source = "../../modules/sqs/LR-06"

  suffix = local.environment
}

module "lr_10_registration_orchestration" {
  source = "../../modules/step_functions/LR-10"

  name         = "LR_10_registration-differences-${local.environment}"
  lr_11_lambda = module.lambda.lr_11_lambda_arn
  lr_12_lambda = module.lambda.lr_12_lambda_arn
  lr_15_lambda = module.lambda.lr_15_lambda_arn
}

module "test_data" {
  # only load test data in the non-prod accounts
  count = local.environment != "prod" ? 1 : 0

  source = "../../modules/test_data"

  suffix       = local.environment
  LR_22_bucket = module.s3.buckets.LR-22.bucket
}
