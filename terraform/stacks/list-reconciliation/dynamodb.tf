module "jobs_table" {
  source          = "../../modules/dynamodb"
  table_name      = "Jobs-${local.environment}"
  table_hash_key  = "Id"
  table_range_key = "PracticeCode"
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

module "jobs_stats_table" {
  source          = "../../modules/dynamodb"
  table_range_key = ""
  table_name      = "JobStats-${local.environment}"
  table_hash_key  = "JobId"
  secondary_index = []
  attributes = [
    {
      name = "JobId"
      type = "S"
    }
  ]
}

module "in_flight_table" {
  source          = "../../modules/dynamodb"
  table_name      = "InFlight-${local.environment}"
  table_hash_key  = "JobId"
  table_range_key = ""
  secondary_index = []
  attributes = [
    {
      name = "JobId"
      type = "S"
    }
  ]
}

module "demographics_table" {
  source          = "../../modules/dynamodb"
  table_name      = "Demographics-${local.environment}"
  table_hash_key  = "Id"
  table_range_key = "JobId"
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

module "demographics_differences_table" {
  source          = "../../modules/dynamodb"
  table_name      = "DemographicsDifferences-${local.environment}"
  table_hash_key  = "Id"
  table_range_key = "JobId"
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

module "errors_table" {
  source          = "../../modules/dynamodb"
  table_name      = "Errors-${local.environment}"
  table_hash_key  = "Id"
  table_range_key = "JobId"
  secondary_index = []
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

module "statuses_table" {
  source          = "../../modules/dynamodb"
  table_name      = "Statuses-${local.environment}"
  table_hash_key  = "Id"
  table_range_key = ""
  secondary_index = []
  attributes = [
    {
      name = "Id"
      type = "S"
    },
  ]
}
