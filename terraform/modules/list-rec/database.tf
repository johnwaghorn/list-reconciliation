locals {
  jobs_gsi = [
    {
      name            = "jobs-id-index",
      hash_key        = "Id"
      projection_type = "ALL"
    }
  ]

  demographics_gsi = [
    {
      name            = "demographics-job_id-index",
      hash_key        = "JobId"
      projection_type = "ALL"
    }
  ]

  demographicsdifferences_gsi = [
    {
      name            = "demographicsdifferences-job_id-index",
      hash_key        = "JobId"
      projection_type = "ALL"
    }
  ]
}

module "Jobs_Table" {
  source          = "../database"
  table_name      = "Jobs-${var.suffix}"
  table_hash_key  = "Id"
  table_range_key = "PracticeCode"
  secondary_index = local.jobs_gsi
  attributes      = var.jobs_attribute
}

module "Jobs_Stats_Table" {
  source          = "../database"
  table_range_key = ""
  table_name      = "JobStats-${var.suffix}"
  table_hash_key  = "JobId"
  secondary_index = []
  attributes      = var.jobs_stats_attribute
}

module "In_Flight_Table" {
  source          = "../database"
  table_name      = "InFlight-${var.suffix}"
  table_hash_key  = "JobId"
  table_range_key = ""
  secondary_index = []
  attributes      = var.in_flight_attribute
}

module "Demographics_Table" {
  source          = "../database"
  table_name      = "Demographics-${var.suffix}"
  table_hash_key  = "Id"
  table_range_key = "JobId"
  secondary_index = local.demographics_gsi
  attributes      = var.demographic_attribute
}

module "Demographics_Differences_Table" {
  source          = "../database"
  table_name      = "DemographicsDifferences-${var.suffix}"
  table_hash_key  = "Id"
  table_range_key = "JobId"
  secondary_index = local.demographicsdifferences_gsi
  attributes      = var.demographic_difference_attribute
}

module "Errors_Table" {
  source          = "../database"
  table_name      = "Errors-${var.suffix}"
  table_hash_key  = "Id"
  table_range_key = "JobId"
  secondary_index = []
  attributes      = var.errors_attribute
}

module "Statuses_Table" {
  source          = "../database"
  table_name      = "Statuses-${var.suffix}"
  table_hash_key  = "Id"
  table_range_key = ""
  secondary_index = []
  attributes      = var.status_attribute
}
