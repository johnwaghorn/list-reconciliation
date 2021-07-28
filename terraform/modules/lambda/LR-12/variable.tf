variable "runtime" {
  type = string
}

variable "package_layer_arn" {
  type = string
}

variable "lambda_name" {
  type = string
}

variable "registrations_output_bucket" {
  type = string
}

variable "registrations_output_bucket_arn" {
  type = string
}

variable "pds_practice_registrations_bucket" {
  type = string
}

variable "pds_practice_registrations_bucket_arn" {
  type = string
}

variable "demographics_table_arn" {
  type = string
}

variable "jobs_table_arn" {
  type = string
}

variable "job_stats_table_arn" {
  type = string
}

variable "errors_table_arn" {
  type = string
}

variable "demographics_table_name" {
  type = string
}

variable "jobs_table_name" {
  type = string
}

variable "job_stats_table_name" {
  type = string
}

variable "errors_table_name" {
  type = string
}

variable "mock_pds_data_bucket_arn" {
  type = string
}

variable "pds_url" {
  type = string
}

variable "pds_api_retries" {
  type    = number
  default = 5
}

variable "lambda_timeout" {
  type = number
}

variable "suffix" {
  type = string
}

variable "lambda_handler" {
  type = string
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
