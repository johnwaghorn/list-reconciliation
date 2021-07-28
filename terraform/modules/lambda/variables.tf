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

variable "mesh_post_office_open" {
  description = "If set to True, messages will be moved from Mesh Inbound to LR-01 Inbound"
  type        = string
}

variable "mesh_post_office_mappings" {
  description = "Mappings of where the Post Office will check messages and deliver them to"
  type        = list(any)
}

variable "mesh_kms_key_alias" {
  description = "The alias of the Mesh KMS encryption key"
  type        = string
}

variable "log_retention_in_days" {
  description = "How many days to retain logs for"
  type        = number

  validation {
    condition     = var.log_retention_in_days >= 1
    error_message = "The log_retention_in_days value must be greater than or equal to 1."
  }
}
