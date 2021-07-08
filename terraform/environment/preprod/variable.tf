variable "runtime" {
  type    = string
  default = "python3.8"
}

variable "lambda_timeout" {
  type    = number
  default = 300
}

variable "region" {
  default = "eu-west-2"
}