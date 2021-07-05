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

  default_tags {
    tags = local.tags
  }
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
