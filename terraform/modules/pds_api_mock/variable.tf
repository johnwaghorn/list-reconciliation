variable "runtime" {
  type = string
}

variable "suffix" {
  type = string
}

variable "data_bucket" {
  type = string
}

variable "data_bucket_arn" {
  type = string
}

variable "data_file" {
  type = string
}

variable "s3_kms_key" {
  type = map(string)
}
