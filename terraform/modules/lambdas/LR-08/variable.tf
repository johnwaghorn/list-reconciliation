variable "runtime" {
  type = string
}

variable "package_layer_arn" {
  type = string
}

variable "patient_sqs" {
  type = string
  default = "Patient_Records.fifo"
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

variable "demographicsdifferences_table_arn" {
  type = string
}

variable "demographics_table_name" {
  type = string
}

variable "errors_table_name" {
  type = string
}

variable "demographicsdifferences_table_name" {
  type = string
}