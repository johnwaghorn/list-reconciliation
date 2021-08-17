variable "suffix" {
  type = string
}

variable "log_retention_in_days" {
  type = string
}

variable "transform_lambda_arn" {
  type = string
}

variable "firehose_failure_bucket_arn" {
  type = string
}

variable "cloudwatch_kms_key" {
  type = map(string)
}

variable "splunk_hec_endpoint" {
  description = "Splunk HEC Endpoint URL"
  type        = string
  default     = "https://hec.splunk.aws.digital.nhs.uk/services/collector"
}
