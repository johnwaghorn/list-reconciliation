locals {
  name               = "list-reconciliation-${local.environment}"
  environment        = "prod"

  tags = {
    TagVersion         = "1"
    Programme          = "SpinePod5"
    Project            = "ListReconciliation"
    DataClassification = "5"
    Environment        = local.environment
    ServiceCategory    = "Silver"
    Tool               = "terraform"
  }
}
