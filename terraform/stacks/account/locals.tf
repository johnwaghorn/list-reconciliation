locals {
  name                = "list-reconciliation-${local.environment}"
  environment         = lower(terraform.workspace)
  data_classification = local.environment == "prod" ? "5" : "1"

  log_retention_in_days = {
    default = 3
    preprod = 14
    prod    = 365
  }

  tags = {
    TagVersion         = "1"
    Programme          = "PCRM"
    Project            = "ListReconciliation"
    DataClassification = local.data_classification
    Environment        = local.environment
    ServiceCategory    = local.environment == "prod" ? "Silver" : "N/A"
    Tool               = "Terraform"
  }
}
