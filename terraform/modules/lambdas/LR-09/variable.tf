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

variable "lr_10_step_function_arn" {
  type = string
}

variable "demographics_table_arn" {
  type = string
}

variable "demographics_table_name" {
  type = string
}

variable "jobs_table_arn" {
  type = string
}

variable "jobs_table_name" {
  type = string
}

variable "job_stats_table_arn" {
  type = string
}

variable "job_stats_table_name" {
  type = string
}

variable "inflight_table_arn" {
  type = string
}

variable "inflight_table_name" {
  type = string
}

variable "errors_table_arn" {
  type = string
}

variable "errors_table_name" {
  type = string
}