locals {
  name                = "list-reconciliation-${local.environment}"
  environment         = lower(terraform.workspace)
  data_classification = local.environment == "prod" ? "5" : "1"

  log_retention_in_days = {
    default = 3
    preprod = 14
    prod    = 365
  }

  terraform_deploy_role_arn = {
    dev     = "arn:aws:iam::092420156801:role/LRTerraformDeploy"
    preprod = "arn:aws:iam::287634746327:role/LRTerraformDeploy"
    # prod = "arn:aws:iam::000000000000:role/LRTerraformDeploy"
  }

  pds_fhir_api_url = {
    default = "https://sandbox.api.service.nhs.uk",
    preprod = "https://int.api.service.nhs.uk"
    # prod    = ""
  }

  mesh_kms_key_alias = {
    default = ""
    preprod = "alias/list-rec-preprod-mesh"
    prod    = "alias/list-rec-prod-mesh"
  }

  send_emails = {
    default = false
    preprod = true
    prod    = true
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
        name = "SupplementaryPdsData"
        inbound = {
          bucket = "list-rec-preprod-mesh"
          key    = "inbound_X26OT179"
        },
        outbound = {
          bucket = module.s3.buckets.LR-20.bucket
          key    = ""
        }
      },
      {
        name = "GpPracticeData"
        inbound = {
          bucket = "list-rec-preprod-mesh"
          key    = "inbound_X26OT181"
        },
        outbound = {
          bucket = module.s3.buckets.LR-01.bucket
          key    = "inbound"
        }
      }
    ]
    prod = []
  }

  lr_09_event_schedule_expression = {
    default = null
    preprod = "rate(5 minutes)"
    prod    = "rate(5 minutes)"
  }

  lr_25_event_schedule_expression = {
    default = null
    preprod = "rate(5 minutes)"
    prod    = "rate(5 minutes)"
  }

  mesh_mappings = {
    default = [
      {
        id = "X26OT181TEST"
        outbound_mappings = [
          {
            dest_mailbox = "X26OT188TEST"
            workflow_id  = "RSLISTRECONCILIATIONPCSE"
          }
        ]
      },
      {
        id = "X26OT178TEST"
        outbound_mappings = [
          {
            dest_mailbox = "INTERNALSPINE"
            workflow_id  = "LISTRECONCILIATIONWORKITEM-Data"
          }
        ]
      },
      {
        id                = "X26OT179TEST"
        outbound_mappings = []
      }
    ]
    preprod = [
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
    prod = []
  }

  lr_07_reserved_concurrent_executions = {
    default = null
    preprod = 300
    prod    = 300
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
