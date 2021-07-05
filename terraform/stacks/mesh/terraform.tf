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

  default_tags {
    tags = local.tags
  }
}

terraform {
  backend "s3" {
    bucket         = "terraform-list-reconciliation-state-mgmt"
    key            = "mesh.tfstate"
    dynamodb_table = "terraform-list-reconciliation-locks"
    region         = "eu-west-2"
    encrypt        = true
    role_arn       = "arn:aws:iam::486319732046:role/LRTerraformBase"
  }
}
