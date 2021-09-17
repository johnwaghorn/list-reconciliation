variable "name" {
  description = ""
  type        = string
}

variable "environment" {
  description = ""
  type        = string
}

variable "kms_cloudwatch_key_arn" {
  description = "KMS Key for Cloudwatch log encryption"
  type        = string
}

variable "runtime" {
  description = ""
  type        = string
  default     = "python3.9"
}

variable "timeout" {
  description = ""
  type        = number
  default     = 3 * 60 # 3 minutes
}

variable "handler" {
  description = ""
  type        = string
  default     = "main.lambda_handler"
}

variable "lambda_layers" {
  description = ""
  type        = list(string)
  default     = []
}

variable "log_retention_in_days" {
  description = "How many days to retain logs for"
  type        = number

  validation {
    condition     = var.log_retention_in_days >= 1
    error_message = "The log_retention_in_days value must be greater than or equal to 1."
  }
}

variable "network_access" {
  description = "[private,public]"
  type        = string
  default     = "private"
}

variable "lambda_invoke_self" {
  description = "allow self invoke"
  type        = bool
  default     = false
}

variable "lambdas_to_invoke" {
  description = "list of lambdas"
  type        = list(string)
  default     = []
}

variable "step_functions_to_invoke" {
  description = "list of step functions"
  type        = list(string)
  default     = []
}

variable "s3_read_only" {
  description = "list of buckets"
  type        = list(string)
  default     = []
}

variable "s3_read_write" {
  description = "list of buckets"
  type        = list(string)
  default     = []
}

variable "dynamodb_read_only" {
  description = "list of tables"
  type        = list(string)
  default     = []
}

variable "dynamodb_read_write" {
  description = "list of tables"
  type        = list(string)
  default     = []
}

variable "kms_read_only" {
  description = "list of keys"
  type        = list(string)
  default     = []
}

variable "kms_read_write" {
  description = "list of keys"
  type        = list(string)
  default     = []
}

variable "ssm_read_only" {
  description = "list of parameters"
  type        = list(string)
  default     = []
}

variable "ssm_read_write" {
  description = "list of parameters"
  type        = list(string)
  default     = []
}

variable "ssm_read_by_path" {
  description = "list of parameter paths"
  type        = list(string)
  default     = []
}

variable "environment_variables" {
  description = "object"
  default     = {}
  type        = map(string)
}

variable "event_schedule_expression" {
  description = ""
  default     = null
}

variable "reserved_concurrent_executions" {
  description = ""
  default     = null
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "vpc_subnet_ids" {
  description = "Subnet IDs for Lambda to execute in"
  type        = list(string)
  default     = []
}

variable "security_group_egresses_length" {
  description = "Hack for creating Security Group Egresses"
  type        = number
  default     = 0
}

variable "security_group_egresses" {
  description = "Security Group Egresses"
  type        = list(object({ ids = list(string), port = number }))
  default     = []
}

variable "cidr_block_egresses_length" {
  description = "Hack for creating CIDR Block Egresses"
  type        = number
  default     = 0
}

variable "cidr_block_egresses" {
  description = "CIDR Block Egresses"
  type        = list(object({ cidr_block = string, port = number }))
  default     = []
}

variable "prefix_list_egresses_length" {
  description = "Hack for creating Prefix List Egresses"
  type        = number
  default     = 0
}

variable "prefix_list_egresses" {
  description = "Prefix List Egresses"
  type        = list(object({ id = string, port = number }))
  default     = []
}
