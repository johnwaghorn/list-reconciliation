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
