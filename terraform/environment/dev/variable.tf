variable "prefix" {
  type    = string
  default = "NHS-list-rec"
}

variable "runtime" {
  type    = string
  default = "python3.8"
}

variable "lambda_timeout" {
  type    = number
  default = 300
}