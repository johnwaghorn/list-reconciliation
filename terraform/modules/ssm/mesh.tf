resource "aws_ssm_parameter" "mesh_mappings" {
  name      = "/${var.prefix}/mesh/mesh_mappings"
  overwrite = true
  type      = "String"
  value     = jsonencode(var.mesh_mappings)
}


resource "aws_ssm_parameter" "listrec_pcse_workflow" {
  name      = "/${var.prefix}/mesh/listrec_pcse_workflow"
  overwrite = true
  type      = "String"
  value     = "RSLISTRECONCILIATIONPCSE"
}


resource "aws_ssm_parameter" "listrec_spinedsa_workflow" {
  name      = "/${var.prefix}/mesh/listrec_spinedsa_workflow"
  overwrite = true
  type      = "String"
  value     = "LISTRECONCILIATIONWORKITEM-Data"
}
