variable "runtime" {
  type    = string
  default = "python3.9"
}

variable "lambda_timeout" {
  type = number
}

variable "lambda_layers" {
  type = list(string)
}

variable "pds_base_url" {
  type = string
}

variable "env_vars" {
  type    = map(string)
  default = {}
}

variable "lambda_name" {
  type = string
}

variable "lambda_handler" {
  type = string
}

variable "lr_08_lambda" {
  type = string
}

variable "demographics_table_arn" {
  type = string
}

variable "demographics_table_name" {
  type = string
}

variable "mock_pds_data_bucket_arn" {
  type = string
}

variable "suffix" {
  type = string
}

variable "lr_06_bucket_arn" {
  type = string
}

variable "lr_06_bucket" {
  type = string
}

variable "cloudwatch_kms_key" {
  type = map(string)
}

variable "dynamodb_kms_key" {
  type = map(string)
}

variable "s3_kms_key" {
  type = map(string)
}

variable "log_retention_in_days" {
  type = number
}


variable "ssm_kms_key" {
  type = map(string)
}

variable "pds_ssm_prefix" {
  type = string
}

variable "pds_ssm_access_token" {
  type = string
}

variable "lr_07_reserved_concurrent_executions" {
  description = "Number of Lambda Reserved Concurrent Executions"
  type        = number
}
