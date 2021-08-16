variable "runtime" {
  type    = string
  default = "python3.9"
}

variable "lambda_layers" {
  type = list(string)
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

variable "demographics_table_name" {
  type = string
}

variable "jobs_table_name" {
  type = string
}

variable "job_stats_table_name" {
  type = string
}

variable "mock_pds_data_bucket_arn" {
  type = string
}

variable "pds_base_url" {
  description = "PDS FHIR API base url"
  type        = string
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
