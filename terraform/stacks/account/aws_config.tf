module "aws_config" {
  source = "../../modules/aws_config"

  environment = local.environment
}
