module "jobs" {
  source                         = "../../modules/dynamodb"
  table_name                     = "Jobs-${local.environment}"
  table_hash_key                 = "Id"
  table_range_key                = "PracticeCode"
  point_in_time_recovery_enabled = true
  kms_key_arn                    = module.kms["dynamodb"].output.arn
  secondary_index = [
    {
      name            = "jobs-id-index",
      hash_key        = "Id"
      projection_type = "ALL"
    }
  ]
  attributes = [
    {
      name = "Id"
      type = "S"
    },
    {
      name = "PracticeCode"
      type = "S"
    }
  ]
}

module "jobs_stats" {
  source                         = "../../modules/dynamodb"
  table_name                     = "JobStats-${local.environment}"
  table_hash_key                 = "JobId"
  point_in_time_recovery_enabled = true
  kms_key_arn                    = module.kms["dynamodb"].output.arn
  attributes = [
    {
      name = "JobId"
      type = "S"
    }
  ]
}

#tfsec:ignore:aws-dynamodb-enable-recovery
module "in_flight" {
  source         = "../../modules/dynamodb"
  table_name     = "InFlight-${local.environment}"
  table_hash_key = "JobId"
  kms_key_arn    = module.kms["dynamodb"].output.arn
  attributes = [
    {
      name = "JobId"
      type = "S"
    }
  ]
}

#tfsec:ignore:aws-dynamodb-enable-recovery
module "demographics" {
  source          = "../../modules/dynamodb"
  table_name      = "Demographics-${local.environment}"
  table_hash_key  = "Id"
  table_range_key = "JobId"
  kms_key_arn     = module.kms["dynamodb"].output.arn
  secondary_index = [
    {
      name            = "demographics-job_id-index",
      hash_key        = "JobId"
      projection_type = "ALL"
    }
  ]
  attributes = [
    {
      name = "Id"
      type = "S"
    },
    {
      name = "JobId"
      type = "S"
    }
  ]
}

#tfsec:ignore:aws-dynamodb-enable-recovery
module "demographics_differences" {
  source          = "../../modules/dynamodb"
  table_name      = "DemographicsDifferences-${local.environment}"
  table_hash_key  = "Id"
  table_range_key = "JobId"
  kms_key_arn     = module.kms["dynamodb"].output.arn
  secondary_index = [
    {
      name            = "demographicsdifferences-job_id-index",
      hash_key        = "JobId"
      projection_type = "ALL"
    }
  ]
  attributes = [
    {
      name = "Id"
      type = "S"
    },
    {
      name = "JobId"
      type = "S"
    }
  ]
}
