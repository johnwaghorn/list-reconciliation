variable "runtime" {
  type = string
}

variable "lambda_timeout" {
  type = number
}

variable "package_layer_arn" {
  type = string
}

variable "pds_url" {
  type = string
}

variable "patient_sqs" {
  type    = string
  default = "Patient_Records.fifo"
}

variable "patient_sqs_arn" {
  type = string
}

variable "env_vars" {
  type    = map(string)
  default = {}
}

variable "lambda_name" {
  type = string
}

variable "lambda_handler" {
  type = string
}
variable "lr_08_lambda" {
  type = string
}

variable "demographics_table_arn" {
  type = string
}

variable "errors_table_arn" {
  type = string
}

variable "demographics_table_name" {
  type = string
}

variable "errors_table_name" {
  type = string
}

variable "mock_pds_data_bucket_arn" {
  type = string
}

variable "suffix" {
  type = string
}

variable "dynamodb_kms_key" {
  type = map(string)
}

variable "s3_kms_key" {
  type = map(string)
}
