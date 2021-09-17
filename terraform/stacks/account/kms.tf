module "kms" {
  source = "../../modules/kms_key"
  for_each = toset([
    "cloudwatch",
    "dynamodb",
  ])

  name        = each.key
  environment = local.environment
}
