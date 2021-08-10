data "aws_kms_key" "mesh_kms" {
  count  = local.environment == "prod" ? 1 : 0
  key_id = "alias/list-rec-${local.environment}-mesh"
}
