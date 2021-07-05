locals {
  tags = {
    TagVersion         = "1"
    Programme          = "SpinePod5"
    Project            = "ListReconciliationMesh"
    DataClassification = local.data_clasification
    Environment        = local.environment
    ServiceCategory    = local.environment == "prod" ? "Silver" : "N/A"
    Tool               = "terraform"
  }
}
