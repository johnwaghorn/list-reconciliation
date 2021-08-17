module "firehose" {
  source = "../../modules/firehose"

  cloudwatch_kms_key          = module.kms["cloudwatch"].output
  suffix                      = local.environment
  transform_lambda_arn        = module.lambda.lr_29_lambda_arn
  firehose_failure_bucket_arn = module.s3.buckets.lr_30.arn
  log_retention_in_days       = try(local.log_retention_in_days[local.environment], local.log_retention_in_days["default"])
}
