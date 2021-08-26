terraform {
  required_version = ">= 1.0.0"

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
    # Try to find a role matching the current environment, if there isn't one default to the dev role
    role_arn = try(local.terraform_deploy_role_arn[terraform.workspace], local.terraform_deploy_role_arn["dev"])
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
