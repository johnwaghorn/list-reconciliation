variable "name" {
  type = string
}

variable "environment" {
  type = string
}

variable "step_function_definition" {
  description = "JSON of the Amazon States Language definition of the state machine"
  type        = string
}

variable "lambdas_to_invoke" {
  description = "Lambdas that the Step Function is able to invoke"
  type        = list(string)
  default     = []
}
