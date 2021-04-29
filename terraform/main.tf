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

resource "aws_dynamodb_table" "In_Flight_Table" {
  name = "In_Flight"
  hash_key = "Practice_Code"
  billing_mode = "PROVISIONED"
  write_capacity = 5
  read_capacity = 5
  stream_enabled = false

  attribute {
    name = "Practice_Code"
    type = "S"
  }
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