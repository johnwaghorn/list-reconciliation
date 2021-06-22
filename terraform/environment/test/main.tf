terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region  = "eu-west-2"
  profile = "default"
}

terraform {
  backend "s3" {
    bucket         = "terraform-list-reconciliation-state"
    key            = "workspaces/terraform.tfstate"
    dynamodb_table = "terraform-list-reconciliation-locks"
    profile        = "default"
    region         = "eu-west-2"
    encrypt        = true
  }
}

module "List-Recon" {
  source      = "../../modules/list-rec"
  pds_url     = "s3://mock-pds-data/pds_api_data.csv"
  patient_sqs = "Patient_Records.fifo"
  runtime     = var.runtime
}