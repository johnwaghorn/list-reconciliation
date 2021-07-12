module "list_rec" {
  source = "../../modules/list-rec"

  suffix         = local.environment
  pds_url        = "pds_api_data.csv"
  patient_sqs    = "Patient_Records.fifo"
  runtime        = "python3.8"
  lambda_handler = "main.lambda_handler"

  dynamodb_tables = {
    jobs = {
      name = module.jobs_table.dynamo_table_name
      arn  = module.jobs_table.dynamo_table_arn
    }
    demographics = {
      name = module.demographics_table.dynamo_table_name
      arn  = module.demographics_table.dynamo_table_arn
    }
    inflight = {
      name = module.in_flight_table.dynamo_table_name
      arn  = module.in_flight_table.dynamo_table_arn
    }
    errors = {
      name = module.errors_table.dynamo_table_name
      arn  = module.errors_table.dynamo_table_arn
    }
    demographics_differences = {
      name = module.demographics_differences_table.dynamo_table_name
      arn  = module.demographics_differences_table.dynamo_table_arn
    }
    jobs_stats = {
      name = module.jobs_stats_table.dynamo_table_name
      arn  = module.jobs_stats_table.dynamo_table_arn
    }
    statuses = {
      name = module.statuses_table.dynamo_table_name
      arn  = module.statuses_table.dynamo_table_arn
    }
  }
}

module "test_data" {
  # only load test data in the non-prod accounts
  count = local.environment != "prod" ? 1 : 0

  source = "../../modules/test-data"

  LR_22_bucket  = module.list_rec.LR_22_bucket
  mock_pds_data = module.list_rec.mock_pds_data
}
