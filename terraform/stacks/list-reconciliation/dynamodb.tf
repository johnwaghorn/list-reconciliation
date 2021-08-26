module "lr_03_jobs" {
  source = "../../modules/dynamodb_table"

  table_name      = "${local.environment}-lr-03-jobs"
  table_hash_key  = "Id"
  table_range_key = "PracticeCode"
  kms_key_arn     = module.kms["dynamodb"].key.arn

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

  secondary_index = [
    {
      name            = "JobId",
      hash_key        = "Id"
      projection_type = "ALL"
    }
  ]
}

module "lr_28_jobs_stats" {
  source = "../../modules/dynamodb_table"

  table_name     = "${local.environment}-lr-28-job-stats"
  table_hash_key = "JobId"
  kms_key_arn    = module.kms["dynamodb"].key.arn

  attributes = [
    {
      name = "JobId"
      type = "S"
    }
  ]
}

#tfsec:ignore:aws-dynamodb-enable-recovery
module "lr_29_in_flight" {
  source = "../../modules/dynamodb_table"

  table_name                     = "${local.environment}-lr-29-in-flight"
  table_hash_key                 = "JobId"
  kms_key_arn                    = module.kms["dynamodb"].key.arn
  point_in_time_recovery_enabled = false

  attributes = [
    {
      name = "JobId"
      type = "S"
    }
  ]
}

#tfsec:ignore:aws-dynamodb-enable-recovery
module "lr_30_demographics" {
  source = "../../modules/dynamodb_table"

  table_name                     = "${local.environment}-lr-30-demographics"
  table_hash_key                 = "Id"
  table_range_key                = "JobId"
  kms_key_arn                    = module.kms["dynamodb"].key.arn
  point_in_time_recovery_enabled = false

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

  secondary_index = [
    {
      name            = "JobId",
      hash_key        = "JobId"
      projection_type = "ALL"
    }
  ]
}

#tfsec:ignore:aws-dynamodb-enable-recovery
module "lr_31_demographics_differences" {
  source = "../../modules/dynamodb_table"

  table_name                     = "${local.environment}-lr-31-demographics-differences"
  table_hash_key                 = "Id"
  table_range_key                = "JobId"
  kms_key_arn                    = module.kms["dynamodb"].key.arn
  point_in_time_recovery_enabled = false

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

  secondary_index = [
    {
      name            = "JobId",
      hash_key        = "JobId"
      projection_type = "ALL"
    }
  ]
}
