variable "environment" {
  description = "Environment"
  type        = string
}

variable "endpoint" {
  description = "Which endpoint"
  type        = string
}

variable "endpoint_type" {
  description = "Type of endpoint"
  type        = string

  validation {
    condition     = var.endpoint_type == "Gateway" || var.endpoint_type == "GatewayLoadBalancer" || var.endpoint_type == "Interface"
    error_message = "The endpoint_type value must be one of \"Gateway\", \"GatewayLoadBalancer\" or \"Interface\"."
  }
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "vpc_route_table_ids" {
  description = "Route Table IDs for Gateway type endpoints"
  type        = list(string)
  default     = []
}

variable "vpc_subnet_ids" {
  description = "Subnet IDs for non-Gateway type endpoints"
  type        = list(string)
  default     = []
}

variable "private_dns_enabled" {
  description = "Enable Private DNS"
  type        = bool
  default     = true
}

variable "auto_accept" {
  description = "Enable Auto Accept"
  type        = bool
  default     = false
}

variable "policy" {
  description = "Endpoint IAM Policy"
  type        = string
  default     = null
}
