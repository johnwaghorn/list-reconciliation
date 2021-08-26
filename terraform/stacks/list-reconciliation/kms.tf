module "kms" {
  source = "../../modules/kms_key"
  for_each = toset([
    "cloudwatch",
    "dynamodb",
    "ssm",
    "s3",
    "mesh",
  ])

  name        = each.key
  environment = local.environment
}
