data "aws_caller_identity" "current" {}

data "aws_kms_alias" "mesh" {
  count = var.mesh_kms_key_alias != "" ? 1 : 0

  name = var.mesh_kms_key_alias
}
