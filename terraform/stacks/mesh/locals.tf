locals {
  name               = "list-rec-${local.environment}"
  environment        = terraform.workspace
  data_clasification = local.environment == "prod" ? "5" : "1"

  terraform_deploy_role_arn = {
    dev     = "arn:aws:iam::092420156801:role/LRTerraformDeploy"
    preprod = "arn:aws:iam::287634746327:role/LRTerraformDeploy"
    # prod = "arn:aws:iam::000000000000:role/LRTerraformDeploy"
  }

  mesh_mailboxes = {
    default = [
      {
        id = "X26OT178"
        outbound_mappings = [
          {
            dest_mailbox = "X26OT179"
            workflow_id  = "TESTWORKFLOW"
          }
        ]
      },
      {
        id = "X26OT179"
        outbound_mappings = [
          {
            dest_mailbox = "X26OT178"
            workflow_id  = "TESTWORKFLOW"
          }
        ]
      }
    ]
  }

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
