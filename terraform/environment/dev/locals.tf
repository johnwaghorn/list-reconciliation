locals {
  name               = "list-reconciliation-${local.environment}"
  environment        = lower(terraform.workspace)

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
