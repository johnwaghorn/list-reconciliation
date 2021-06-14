variable "runtime" {
  type = string
}

variable "patient_sqs" {
  type = string
}

variable "pds_url" {
  type = string
}

variable "jobs_attribute" {
  default = [
    {
      name = "Id"
      type = "S"
    },
    {
      name = "PracticeCode"
      type = "S"
    }
  ]
  type = list(object({
    name = string,
    type = string
  }))
}

variable "jobs_stats_attribute" {
  default = [
    {
      name = "JobId"
      type = "S"
    }]
}

variable "in_flight_attribute" {
  default = [
    {
      name = "JobId"
      type = "S"
    }]
}

variable "demographic_attribute" {
  default = [
    {
      name = "Id"
      type = "S"
    },
    {
      name = "JobId"
      type = "S"
    }
  ]
}

variable "demographic_difference_attribute" {
  default = [
    {
      name = "Id"
      type = "S"
    },
    {
      name = "JobId"
      type = "S"
    }
        ]
}

variable "errors_attribute" {
  default = [
    {
      name = "Id"
      type = "S"
    },
    {
      name = "JobId"
      type = "S"
    }]
}

variable "status_attribute" {
  default = [
    {
      name = "Id"
      type = "S"
    },
  ]
}