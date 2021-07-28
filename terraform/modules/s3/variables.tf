variable "suffix" {
  type = string
}

variable "force_destroy" {
  type    = bool
  default = false
}

variable "kms_key_arn" {
  type = string
}

variable "log_retention_in_days" {
  description = "How many days to retain logs for"
  type        = number

  validation {
    condition     = var.log_retention_in_days >= 1
    error_message = "The log_retention_in_days value must be greater than or equal to 1."
  }
}
