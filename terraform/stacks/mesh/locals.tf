locals {
  name                = "list-rec-${local.environment}"
  environment         = terraform.workspace
  data_classification = local.environment == "prod" ? "5" : "1"

  terraform_deploy_role_arn = {
    dev     = "arn:aws:iam::092420156801:role/LRTerraformDeploy"
    preprod = "arn:aws:iam::287634746327:role/LRTerraformDeploy"
    # prod = "arn:aws:iam::000000000000:role/LRTerraformDeploy"
  }

  mesh_mailboxes = {
    default = [
      {
        id = "X26OT181"
        outbound_mappings = [
          {
            dest_mailbox = "X26OT188"
            workflow_id  = "RSLISTRECONCILIATIONPCSE"
          }
        ]
      },
      {
        id = "X26OT178"
        outbound_mappings = [
          {
            dest_mailbox = "INTERNALSPINE"
            workflow_id  = "LISTRECONCILIATIONWORKITEM-Data"
          }
        ]
      },
      {
        id                = "X26OT179"
        outbound_mappings = []
      }
    ]
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
