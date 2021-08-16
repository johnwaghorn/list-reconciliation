variable "runtime" {
  type    = string
  default = "python3.9"
}

variable "lambda_name" {
  type = string
}

variable "package_layer_arn" {
  type = string
}

variable "lr_01_inbound_folder" {
  type = string
}

variable "lr_01_failed_folder" {
  type = string
}

variable "source_bucket" {
  type = string
}

variable "source_bucket_arn" {
  type = string
}

variable "jobs_table_arn" {
  type = string
}

variable "in_flight_table_arn" {
  type = string
}

variable "jobs_table_name" {
  type = string
}

variable "in_flight_table_name" {
  type = string
}

variable "suffix" {
  type = string
}

variable "lr_24_lambda_arn" {
  type = string
}

variable "lambda_handler" {
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

variable "lr_04_lambda_arn" {
  type = string
}

variable "log_retention_in_days" {
  type = number
}
