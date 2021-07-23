variable "runtime" {
  type = string
}

variable "lambda_name" {
  type = string
}

variable "package_layer_arn" {
  type = string
}

variable "source_bucket" {
  type = string
}

variable "source_bucket_arn" {
  type = string
}

variable "errors_table_arn" {
  type = string
}

variable "errors_table_name" {
  type = string
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