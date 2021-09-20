module "pds_api_mock" {
  source = "../../modules/pds_api_mock"
  count  = local.environment == "prod" ? 0 : 1

  name                         = "pds-api-mock"
  environment                  = local.environment
  pds_api_mock_lambda_function = module.pds_api_mock_lambda[0].lambda
  vpc_id                       = module.vpc.vpc_id
  vpc_subnet_ids               = module.vpc.intra_subnets
}

module "packages" {
  source = "../../modules/lambda_layer"
  count  = local.environment == "prod" ? 0 : 1

  name       = "packages_layer_${local.environment}"
  source_dir = "packages_layer"
}

module "pds_api_mock_dependencies_layer" {
  source = "../../modules/lambda_layer"
  count  = local.environment == "prod" ? 0 : 1

  name       = "pds_api_mock_dependencies_layer_${local.environment}"
  source_dir = "pds_api_mock_dependencies_layer"
}

module "pds_api_mock_lambda" {
  source = "../../modules/lambda_function"
  count  = local.environment == "prod" ? 0 : 1

  name                   = "pds_api_mock"
  environment            = local.environment
  kms_cloudwatch_key_arn = module.kms["cloudwatch"].key.arn
  vpc_id                 = module.vpc.vpc_id
  vpc_subnet_ids         = module.vpc.intra_subnets

  prefix_list_egresses_length = 1
  prefix_list_egresses = [
    { id = module.dynamodb_endpoint.endpoint.prefix_list_id, port = 443 }
  ]
  security_group_egresses_length = 2
  security_group_egresses = [
    { ids = [module.cloudwatch_endpoint.security_group.id], port = 443 },
    { ids = [module.kms_endpoint.security_group.id], port = 443 },
  ]

  dynamodb_read_write   = [module.pds_api_mock_table[0].table.arn]
  kms_read_write        = [module.kms["dynamodb"].key.arn]
  lambda_layers         = [module.packages[0].layer.arn, module.pds_api_mock_dependencies_layer[0].layer.arn]
  log_retention_in_days = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
}

module "pds_api_mock_table" {
  source = "../../modules/dynamodb_table"
  count  = local.environment == "prod" ? 0 : 1

  table_name     = "pds-api-mock"
  table_hash_key = "nhs_number"
  kms_key_arn    = module.kms["dynamodb"].key.arn

  attributes = [
    {
      name = "nhs_number"
      type = "S"
    }
  ]
}
