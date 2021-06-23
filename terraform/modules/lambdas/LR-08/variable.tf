variable "runtime" {
  type = string
}

variable "lambda_timeout" {
  type = number
}

variable "package_layer_arn" {
  type = string
}

variable "lambda_name" {
  type = string
}

variable "demographics_table_arn" {
  type = string
}

variable "errors_table_arn" {
  type = string
}

variable "demographics_differences_table_arn" {
  type = string
}

variable "demographics_table_name" {
  type = string
}

variable "errors_table_name" {
  type = string
}

variable "demographics_differences_table_name" {
  type = string
}

variable "suffix" {
  type = string
}