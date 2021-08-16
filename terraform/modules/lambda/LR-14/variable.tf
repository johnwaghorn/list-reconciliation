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

variable "demographics_differences_table_arn" {
  type = string
}

variable "jobs_table_arn" {
  type = string
}

variable "job_stats_table_arn" {
  type = string
}

variable "demographics_differences_table_name" {
  type = string
}

variable "jobs_table_name" {
  type = string
}

variable "job_stats_table_name" {
  type = string
}

variable "mesh_send_bucket" {
  type = string
}

variable "mesh_send_bucket_arn" {
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

variable "ssm_kms_key" {
  type = map(string)
}

variable "mesh_kms_key" {
  type = map(string)
}

variable "mesh_ssm" {
  type = string
}

variable "email_ssm" {
  type = string
}

variable "pcse_email" {
  type = string
}

variable "listrec_email" {
  type = string
}

variable "log_retention_in_days" {
  type = string
}

variable "send_emails" {
  description = "Toggle to enable actual sending of emails"
  type        = bool
}
