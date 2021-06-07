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
