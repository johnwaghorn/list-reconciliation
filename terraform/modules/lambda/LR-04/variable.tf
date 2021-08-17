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

variable "email_ssm" {
  type = string
}

variable "pcse_email" {
  type = string
}

variable "listrec_email" {
  type = string
}

variable "ssm_kms_key" {
  type = map(string)
}

