variable "runtime" {
  type = string
}

variable "package_layer_arn" {
  type = string
}

variable "lambda_name" {
  type = string
}

variable "mesh_send_bucket_arn" {
  type = string
}

variable "mesh_send_bucket" {
  type = string
}

variable "registrations_output_bucket" {
  type = string
}

variable "registrations_output_bucket_arn" {
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

variable "demographics_differences_table_name" {
  type = string
}

variable "demographics_differences_table_arn" {
  type = string
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
