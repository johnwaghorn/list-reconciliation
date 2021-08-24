output "environment" {
  value = local.environment
}

output "region" {
  value = "eu-west-2"
}

output "lr_01_bucket" {
  value = module.s3.buckets.LR-01.bucket
}

output "lr_02_lambda" {
  value = module.lambda.lr_02_lambda
}

output "lr_02_lambda_arn" {
  value = module.lambda.lr_02_lambda_arn
}

output "lr_04_lambda" {
  value = module.lambda.lr_04_lambda
}

output "lr_04_lambda_arn" {
  value = module.lambda.lr_04_lambda_arn
}

output "lr_07_lambda" {
  value = module.lambda.lr_07_lambda
}

output "lr_07_lambda_arn" {
  value = module.lambda.lr_07_lambda_arn
}

output "lr_08_lambda" {
  value = module.lambda.lr_08_lambda
}

output "lr_08_lambda_arn" {
  value = module.lambda.lr_08_lambda_arn
}

output "lr_09_lambda" {
  value = module.lambda.lr_09_lambda
}

output "lr_10_sfn" {
  value = module.lr_10_registration_orchestration.arn
}

output "lr_10_sfn_arn" {
  value = module.lr_10_registration_orchestration.arn
}

output "lr_11_lambda" {
  value = module.lambda.lr_11_lambda
}

output "lr_11_lambda_arn" {
  value = module.lambda.lr_11_lambda_arn
}

output "jobs_table" {
  value = module.jobs.dynamo_table_name
}

output "demographic_table" {
  value = module.demographics.dynamo_table_name
}

output "in_flight_table" {
  value = module.in_flight.dynamo_table_name
}

output "demographics_difference_table" {
  value = module.demographics_differences.dynamo_table_name
}

output "jobs_stats_table" {
  value = module.jobs_stats.dynamo_table_name
}

output "lr_12_lambda" {
  value = module.lambda.lr_12_lambda
}

output "lr_13_bucket" {
  value = module.s3.buckets.LR-13.bucket
}

output "lr_22_bucket" {
  value = module.s3.buckets.LR-22.bucket
}

output "lr_15_lambda" {
  value = module.lambda.lr_15_lambda
}

output "lr_25_lambda" {
  value = module.lambda.lr_25_lambda
}

output "lr_06_bucket" {
  value = module.s3.buckets.LR-06.bucket
}

output "LR-24-lambda" {
  value = module.lambda.lr_24_lambda
}

output "LR_25_lambda" {
  value = module.lambda.lr_25_lambda
}

output "LR_25_lambda_arn" {
  value = module.lambda.lr_25_lambda_arn
}

output "lr_26_bucket" {
  value = module.s3.buckets.LR-26.bucket
}

output "lr_20_bucket" {
  value = module.s3.buckets.LR-20.bucket
}

output "mesh_bucket" {
  value = module.s3.buckets.mesh_bucket.bucket
}

output "mesh_inbound" {
  value = "inbound_${try(local.mesh_mappings[local.environment][0].id, local.mesh_mappings["default"][0].id)}"
}

output "pds_url" {
  value = try(local.pds_fhir_api_url[local.environment], local.pds_fhir_api_url["default"])
}
