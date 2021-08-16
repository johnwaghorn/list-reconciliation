variable "runtime" {
  type    = string
  default = "python3.9"
}

variable "lambda_name" {
  type = string
}

variable "package_layer_arn" {
  type = string
}

variable "suffix" {
  type = string
}

variable "mesh_post_office_open" {
  description = "If set to True, messages will be moved from Mesh Inbound to LR-01 Inbound"
  # Use a string here to match the Python type
  type    = string
  default = "False"

  validation {
    condition     = var.mesh_post_office_open == "True" || var.mesh_post_office_open == "False"
    error_message = "The mesh_post_office_open value must be either \"True\" or \"False\"."
  }
}

variable "mesh_post_office_mappings" {
  description = "Mappings of where the Post Office will check messages and deliver them to"
  type = list(
    object({
      name = string
      inbound = object({
        bucket = any,
        key    = string
      })
      outbound = object({
        bucket = any,
        key    = string
      })
    })
  )
  default = []

  validation {
    condition = alltrue([
      for mapping in var.mesh_post_office_mappings : can(regex("[0-9A-Za-z]*", mapping.name))
    ])
    error_message = "The mapping names in mesh_post_office_mappings value must satisfies the regular expression \"[0-9A-Za-z]*\"."
  }
}

variable "lr_25_event_schedule_expression" {
  description = "How often should the Post Office attempt to deliver Mesh messages"
  type        = string

  validation {
    condition     = var.lr_25_event_schedule_expression == null || can(regex("^rate\\([0-9][0-9]?[0-9]? (minute|minutes|hour|hours|day|days)\\)$", var.lr_25_event_schedule_expression))
    error_message = "The lr_25_event_schedule_expression value must be a valid Rate Expression."
  }
}

variable "mesh_kms_key_alias" {
  description = "The alias of the Mesh KMS encryption key"
  type        = string
}

variable "cloudwatch_kms_key" {
  type = map(string)
}

variable "s3_kms_key" {
  type = map(string)
}

variable "log_retention_in_days" {
  type = number
}
