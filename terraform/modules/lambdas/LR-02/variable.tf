variable "runtime" {
  type = string
}

variable "lambda_name" {
  type = string
}

variable "patient_sqs" {
  type = string
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

variable "source_bucket" {
  type = string
}
