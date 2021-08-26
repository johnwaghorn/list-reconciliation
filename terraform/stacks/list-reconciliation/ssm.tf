# TODO rename?
module "list_rec_email_password" {
  source = "../../modules/ssm_parameter"

  name                 = "email/list_rec_email_password"
  environment          = local.environment
  ssm_kms_arn          = module.kms["ssm"].key.arn
  ignore_value_changes = true
}

module "mesh_post_office_open" {
  source = "../../modules/ssm_parameter"

  name                 = "mesh/mesh_post_office_open"
  environment          = local.environment
  ssm_kms_arn          = module.kms["ssm"].key.arn
  type                 = "String"
  value                = try(local.mesh_post_office_open[local.environment], local.mesh_post_office_open["default"])
  ignore_value_changes = true
}

module "mesh_mappings" {
  source = "../../modules/ssm_parameter"

  name        = "mesh/mesh_mappings"
  environment = local.environment
  type        = "String"
  ssm_kms_arn = module.kms["ssm"].key.arn
  value       = jsonencode(try(local.mesh_mappings[local.environment], local.mesh_mappings["default"]))
}

module "listrec_pcse_workflow" {
  source = "../../modules/ssm_parameter"

  name        = "mesh/listrec_pcse_workflow"
  environment = local.environment
  ssm_kms_arn = module.kms["ssm"].key.arn
  type        = "String"
  value       = "RSLISTRECONCILIATIONPCSE"
}

module "listrec_spinedsa_workflow" {
  source = "../../modules/ssm_parameter"

  name        = "mesh/listrec_spinedsa_workflow"
  environment = local.environment
  ssm_kms_arn = module.kms["ssm"].key.arn
  type        = "String"
  value       = "LISTRECONCILIATIONWORKITEM-Data"
}

# TODO check name
module "pds_api_private_key" {
  source = "../../modules/ssm_parameter"

  name                 = "pds/pds_api_private_key"
  environment          = local.environment
  ssm_kms_arn          = module.kms["ssm"].key.arn
  ignore_value_changes = true
}

# TODO check name
module "pds_api_access_token" {
  source = "../../modules/ssm_parameter"

  name                 = "pds/pds_api_access_token"
  environment          = local.environment
  ssm_kms_arn          = module.kms["ssm"].key.arn
  ignore_value_changes = true
}

# TODO check name
module "pds_fhir_app_key" {
  source = "../../modules/ssm_parameter"

  name                 = "pds/pds_fhir_app_key"
  environment          = local.environment
  ssm_kms_arn          = module.kms["ssm"].key.arn
  ignore_value_changes = true
}
