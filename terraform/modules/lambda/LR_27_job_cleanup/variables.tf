variable "runtime" {
  type = string
}

variable "lambda_name" {
  type = string
}

variable "package_layer_arn" {
  type = string
}

variable "suffix" {
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

variable "lr_13_registrations_output_bucket" {
  type = string
}

variable "lr_13_registrations_output_bucket_arn" {
  type = string
}

variable "jobs_table_name" {
  type = string
}

variable "in_flight_table_name" {
  type = string
}

variable "jobs_table_arn" {
  type = string
}

variable "in_flight_table_arn" {
  type = string
}
