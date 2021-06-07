variable "runtime" {
  type = string
}

variable "package_layer_arn" {
  type = string
}

variable "pds_url" {
  type = string
  default = "s3://mock-pds-data/pds_api_data.csv"
}

variable "patient_sqs" {
  type = string
  default = "Patient_Records.fifo"
}

variable "patient_sqs_arn" {
  type = string
}

variable "env_vars" {
  type = map(string)
  default = {}
}

variable "lambda_name" {
  type = string
}

variable "lr_08_lambda" {
  type = string
}
