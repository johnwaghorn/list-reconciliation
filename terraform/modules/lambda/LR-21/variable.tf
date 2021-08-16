variable "runtime" {
  type = string
}

variable "lambda_name" {
  type = string
}

variable "package_layer_arn" {
  type = string
}

variable "supplementary_input_bucket" {
  type = string
}

variable "supplementary_input_bucket_arn" {
  type = string
}

variable "supplementary_output_bucket" {
  type = string
}

variable "supplementary_output_bucket_arn" {
  type = string
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

variable "s3_kms_key" {
  type = map(string)
}

variable "log_retention_in_days" {
  type = number
}
