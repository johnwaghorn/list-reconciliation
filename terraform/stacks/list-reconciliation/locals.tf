locals {
  name                = "list-reconciliation-${local.environment}"
  environment         = lower(terraform.workspace)
  data_classification = local.environment == "prod" ? "5" : "1"

  terraform_deploy_role_arn = {
    dev     = "arn:aws:iam::092420156801:role/LRTerraformDeploy"
    preprod = "arn:aws:iam::287634746327:role/LRTerraformDeploy"
    # prod = "arn:aws:iam::000000000000:role/LRTerraformDeploy"
  }

  mesh_kms_key_alias = {
    default = ""
    preprod = "alias/list-rec-preprod-mesh"
    prod    = "alias/list-rec-prod-mesh"
  }

  mesh_post_office_open = {
    default = "False"
    preprod = "True"
    prod    = "False"
  }

  mesh_post_office_mappings = {
    default = []
    preprod = [
      {
        name = "GPData"
        inbound = {
          bucket = "list-rec-preprod-mesh"
          key    = "inbound_X26OT179"
        },
        outbound = {
          bucket = module.s3.buckets.LR-01.bucket
          key    = "inbound"
        }
      }
    ]
    prod = []
  }

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
