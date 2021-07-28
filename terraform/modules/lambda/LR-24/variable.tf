variable "runtime" {
  type = string
}

variable "package_layer_arn" {
  type = string
}

variable "lambda_name" {
  type = string
}

variable "lr-06-bucket_arn" {
  type = string
}

variable "lr-06-bucket" {
  type = string
}

variable "errors_table_arn" {
  type = string
}

variable "errors_table_name" {
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

variable "log_retention_in_days" {
  type = number
}
