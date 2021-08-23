variable "runtime" {
  type    = string
  default = "python3.9"
}

variable "lambda_timeout" {
  type = number
}

variable "lambda_layers" {
  type = list(string)
}

variable "lambda_name" {
  type = string
}

variable "demographics_table_arn" {
  type = string
}

variable "demographics_differences_table_arn" {
  type = string
}

variable "demographics_table_name" {
  type = string
}

variable "demographics_differences_table_name" {
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

variable "dynamodb_kms_key" {
  type = map(string)
}

variable "s3_kms_key" {
  type = map(string)
}

variable "log_retention_in_days" {
  type = number
}
