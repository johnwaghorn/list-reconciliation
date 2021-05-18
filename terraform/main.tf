terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "eu-west-2"
}

resource "aws_sqs_queue" "Patient_Records_Queue" {
  name = "Patient_Records.fifo"
  fifo_queue = true
  content_based_deduplication = true
  delay_seconds = 0
  max_message_size = 262144 # 256kb
  message_retention_seconds = 345600 # 4 days
  visibility_timeout_seconds = 30
  receive_wait_time_seconds = 0
}