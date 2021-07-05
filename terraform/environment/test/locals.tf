locals {
  name        = "list-reconciliation-${local.environment}"
  environment = "test"

  tags = {
    TagVersion         = "1"
    Programme          = "SpinePod5"
    Project            = "ListReconciliation"
    DataClassification = "1"
    Environment        = local.environment
    ServiceCategory    = "N/A"
    Tool               = "terraform"
  }
}
