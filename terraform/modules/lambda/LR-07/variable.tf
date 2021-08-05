variable "runtime" {
  type = string
}

variable "lambda_timeout" {
  type = number
}

variable "package_layer_arn" {
  type = string
}

variable "pds_url" {
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

variable "errors_table_arn" {
  type = string
}

variable "demographics_table_name" {
  type = string
}

variable "errors_table_name" {
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
