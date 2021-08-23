resource "aws_ssm_parameter" "mesh_post_office_open" {
  name      = "/${local.name}/mesh_post_office_open"
  overwrite = true
  type      = "String"
  value     = var.mesh_post_office_open

  lifecycle {
    ignore_changes = [
      value
    ]
  }
}

resource "aws_ssm_parameter" "mappings" {
  name      = "/${local.name}/mappings"
  overwrite = true
  type      = "String"
  value     = jsonencode(var.mesh_post_office_mappings)
}
