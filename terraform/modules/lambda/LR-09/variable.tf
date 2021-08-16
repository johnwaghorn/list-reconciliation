variable "runtime" {
  type    = string
  default = "python3.9"
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

variable "in_flight_table_arn" {
  type = string
}

variable "in_flight_table_name" {
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

variable "lr_09_event_schedule_expression" {
  description = "How often should LR-09 be called"
  type        = string

  validation {
    condition     = var.lr_09_event_schedule_expression == null || can(regex("^rate\\([0-9][0-9]?[0-9]? (minute|minutes|hour|hours|day|days)\\)$", var.lr_09_event_schedule_expression))
    error_message = "The lr_09_event_schedule_expression value must be a valid Rate Expression."
  }
}

variable "lr_09_job_timeout_hours" {
  description = "Number of hours old that a job is allowed to reach before it's cleaned up"
  type        = number
  default     = 6
}
