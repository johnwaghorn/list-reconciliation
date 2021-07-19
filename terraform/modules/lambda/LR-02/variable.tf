variable "runtime" {
  type = string
}

variable "lambda_name" {
  type = string
}

variable "patient_sqs" {
  type    = string
  default = "Patient_Records.fifo"
}

variable "package_layer_arn" {
  type = string
}

variable "lr_01_inbound_folder" {
  type = string
}

variable "patient_sqs_arn" {
  type = string
}

variable "patient_sqs_name" {
  type = string
}

variable "source_bucket" {
  type = string
}

variable "demographics_table_arn" {
  type = string
}

variable "jobs_table_arn" {
  type = string
}

variable "in_flight_table_arn" {
  type = string
}

variable "errors_table_arn" {
  type = string
}

variable "demographics_table_name" {
  type = string
}

variable "jobs_table_name" {
  type = string
}

variable "in_flight_table_name" {
  type = string
}

variable "errors_table_name" {
  type = string
}

variable "suffix" {
  type = string
}

variable "lambda_handler" {
  type = string
}

variable "dynamodb_kms_key" {
  type = map(string)
}
