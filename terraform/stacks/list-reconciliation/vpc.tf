module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "${local.environment}-vpc"

  azs             = ["eu-west-2a", "eu-west-2b", "eu-west-2c"]
  cidr            = "10.0.0.0/16"
  intra_subnets   = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  public_subnets  = ["10.0.201.0/24", "10.0.202.0/24", "10.0.203.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = false
  one_nat_gateway_per_az = false

  enable_dns_hostnames = true
  enable_dns_support   = true

  # Default security group - ingress/egress rules cleared to deny all
  manage_default_security_group  = true
  default_security_group_ingress = []
  default_security_group_egress  = []

  # VPC Flow Logs (Cloudwatch log group and IAM role will be created)
  enable_flow_log                      = true
  create_flow_log_cloudwatch_log_group = true
  create_flow_log_cloudwatch_iam_role  = true
  flow_log_max_aggregation_interval    = 60
}

module "cloudwatch_endpoint" {
  source = "../../modules/vpc_endpoint"

  environment    = local.environment
  endpoint       = "logs"
  endpoint_type  = "Interface"
  vpc_id         = module.vpc.vpc_id
  vpc_subnet_ids = module.vpc.intra_subnets
}

module "dynamodb_endpoint" {
  source = "../../modules/vpc_endpoint"

  environment         = local.environment
  endpoint            = "dynamodb"
  endpoint_type       = "Gateway"
  vpc_id              = module.vpc.vpc_id
  vpc_route_table_ids = concat(module.vpc.intra_route_table_ids, module.vpc.private_route_table_ids)
}

module "kms_endpoint" {
  source = "../../modules/vpc_endpoint"

  environment    = local.environment
  endpoint       = "kms"
  endpoint_type  = "Interface"
  vpc_id         = module.vpc.vpc_id
  vpc_subnet_ids = module.vpc.intra_subnets
}

module "lambda_endpoint" {
  source = "../../modules/vpc_endpoint"

  environment    = local.environment
  endpoint       = "lambda"
  endpoint_type  = "Interface"
  vpc_id         = module.vpc.vpc_id
  vpc_subnet_ids = module.vpc.intra_subnets
}

module "ssm_endpoint" {
  source = "../../modules/vpc_endpoint"

  environment    = local.environment
  endpoint       = "ssm"
  endpoint_type  = "Interface"
  vpc_id         = module.vpc.vpc_id
  vpc_subnet_ids = module.vpc.intra_subnets
}

module "step_function_endpoint" {
  source = "../../modules/vpc_endpoint"

  environment    = local.environment
  endpoint       = "states"
  endpoint_type  = "Interface"
  vpc_id         = module.vpc.vpc_id
  vpc_subnet_ids = module.vpc.intra_subnets
}

module "s3_endpoint" {
  source = "../../modules/vpc_endpoint"

  environment         = local.environment
  endpoint            = "s3"
  endpoint_type       = "Gateway"
  vpc_id              = module.vpc.vpc_id
  vpc_route_table_ids = concat(module.vpc.intra_route_table_ids, module.vpc.private_route_table_ids)
}
