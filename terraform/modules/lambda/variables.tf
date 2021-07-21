variable "runtime" {
  type = string
}

variable "lambda_timeout" {
  type    = number
  default = 300
}

variable "pds_url" {
  type = string
}

variable "pds_api_retries" {
  type    = number
  default = 5
}

variable "suffix" {
  type = string
}

variable "lambda_handler" {
  type = string
}

variable "dynamodb_tables" {
  type = map(map(string))
}

variable "s3_buckets" {
  type = map(map(string))
}

variable "step_functions" {
  type = map(map(string))
}

variable "mock_pds_data_bucket" {
  type = map(string)
}

variable "dynamodb_kms_key" {
  type = map(string)
}

variable "s3_kms_key" {
  type = map(string)
}
