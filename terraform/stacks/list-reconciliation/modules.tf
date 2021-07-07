module "list-rec" {
  source = "../../modules/list-rec"

  suffix         = local.environment
  pds_url        = "pds_api_data.csv"
  patient_sqs    = "Patient_Records.fifo"
  runtime        = "python3.8"
  lambda_handler = "main.lambda_handler"
}

module "test-data" {
  # only load test data in the non-prod accounts
  count = local.environment != "prod" ? 1 : 0

  source = "../../modules/test-data"

  LR_22_bucket  = module.list-rec.LR_22_bucket
  mock_pds_data = module.list-rec.mock_pds_data
}
