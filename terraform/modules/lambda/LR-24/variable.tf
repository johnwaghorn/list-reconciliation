variable "runtime" {
  type    = string
  default = "python3.9"
}

variable "lambda_layers" {
  type = list(string)
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

variable "lambda_timeout" {
  type = number
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
