variable "name" {
  type = string
}

variable "environment" {
  type = string
}

variable "pds_api_mock_lambda_function" {
  # TODO
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "vpc_subnet_ids" {
  description = "Subnet IDs for Lambda to execute in"
  type        = list(string)
}
