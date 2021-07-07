terraform {
  required_version = ">= 0.15.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "eu-west-2"

  assume_role {
    role_arn = "arn:aws:iam::092420156801:role/LRTerraformDeploy"
  }

  default_tags {
    tags = local.tags
  }
}

terraform {
  backend "s3" {
    bucket         = "terraform-list-reconciliation-state-mgmt"
    key            = "list-reconciliation.tfstate"
    dynamodb_table = "terraform-list-reconciliation-locks"
    region         = "eu-west-2"
    encrypt        = true
    role_arn       = "arn:aws:iam::486319732046:role/LRTerraformBase"
  }
}

module "List-Recon" {
  source         = "../../modules/list-rec"
  pds_url        = "s3://mock-pds-data/pds_api_data.csv"
  patient_sqs    = "Patient_Records.fifo"
  runtime        = var.runtime
  suffix         = local.environment
  lambda_handler = "main.lambda_handler"
}
