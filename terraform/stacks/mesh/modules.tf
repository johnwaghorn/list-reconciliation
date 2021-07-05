module "mesh" {
  source = "git::https://github.com/nhsdigital/spine-core-aws-common.git//terraform/mesh_aws?ref=v0.0.6"

  name_prefix = local.name

  config = {
    environment = local.environment == "prod" ? "production" : "integration"
    verify_ssl  = local.environment == "prod" ? true : false
  }

  mailboxes = try(local.mesh_mailboxes[local.environment], local.mesh_mailboxes["default"])
}
