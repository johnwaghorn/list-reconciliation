variable "runtime" {
  type    = string
  default = "python3.9"
}

variable "lambda_name" {
  type = string
}

variable "lambda_layers" {
  type = list(string)
}

variable "suffix" {
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