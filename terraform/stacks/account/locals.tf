locals {
  name                = "list-reconciliation-${local.environment}"
  environment         = lower(terraform.workspace)
  data_classification = local.environment == "prod" ? "5" : "1"

  tags = {
    TagVersion         = "1"
    Programme          = "SpinePod5"
    Project            = "ListReconciliation"
    DataClassification = local.data_classification
    Environment        = local.environment
    ServiceCategory    = local.environment == "prod" ? "Silver" : "N/A"
    Tool               = "terraform"
  }
}
