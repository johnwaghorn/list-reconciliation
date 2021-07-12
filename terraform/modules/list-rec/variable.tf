variable "runtime" {
  type = string
}

variable "lambda_timeout" {
  type    = number
  default = 300
}

variable "patient_sqs" {
  type = string
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
