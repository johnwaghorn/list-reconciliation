variable "runtime" {
  type = string
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

variable "source_bucket" {
  type = string
}

variable "jobs_table_arn" {
  type = string
}

variable "in_flight_table_arn" {
  type = string
}

variable "errors_table_arn" {
  type = string
}

variable "jobs_table_name" {
  type = string
}

variable "in_flight_table_name" {
  type = string
}

variable "errors_table_name" {
  type = string
}

variable "suffix" {
  type = string
}

variable "lr_24_lambda" {
  type = string
}

variable "lambda_handler" {
  type = string
}

variable "lr_06_bucket" {
  type = string
}

variable "dynamodb_kms_key" {
  type = map(string)
}

variable "s3_kms_key" {
  type = map(string)
}
