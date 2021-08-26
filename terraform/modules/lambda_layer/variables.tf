variable "name" {
  type = string
}

variable "source_dir" {
  type = string
}

variable "compatible_runtimes" {
  type    = list(string)
  default = ["python3.9"]
}
