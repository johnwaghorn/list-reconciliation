locals {
  name               = "list-reconciliation-${local.environment}"
  environment        = terraform.workspace
  data_clasification = local.environment == "prod" ? "5" : "1"

  terraform_deploy_role_arn = {
    dev     = "arn:aws:iam::092420156801:role/LRTerraformDeploy"
    preprod = "arn:aws:iam::287634746327:role/LRTerraformDeploy"
    # prod = "arn:aws:iam::000000000000:role/LRTerraformDeploy"
  }

  tags = {
    TagVersion         = "1"
    Programme          = "SpinePod5"
    Project            = "ListReconciliation"
    DataClassification = local.data_clasification
    Environment        = local.environment
    ServiceCategory    = local.environment == "prod" ? "Silver" : "N/A"
    Tool               = "terraform"
  }
}
