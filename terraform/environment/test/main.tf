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
  suffix      = ""
}

resource "aws_s3_bucket_object" "upload-mock-pds-data" {
  bucket = module.List-Recon.mock_pds_data
  key    = "pds_api_data.csv"
  acl    = "private"
  source = "../../../test/unittests/lambdas/data/pds_api_data.csv"
  etag   = filemd5("../../../test/unittests/lambdas/data/pds_api_data.csv")
}

resource "aws_s3_bucket_object" "upload-test-pds-registration-data-1" {
  bucket = module.List-Recon.LR_22_bucket
  key    = "Y123451.csv"
  acl    = "private"
  source = "../../../test/unittests/lambdas/data/Y123451.csv"
  etag   = filemd5("../../../test/unittests/lambdas/data/Y123451.csv")
}

resource "aws_s3_bucket_object" "upload-test-pds-registration-data-2" {
  bucket = module.List-Recon.LR_22_bucket
  key    = "Y123452.csv"
  acl    = "private"
  source = "../../../test/unittests/lambdas/data/Y123452.csv"
  etag   = filemd5("../../../test/unittests/lambdas/data/Y123452.csv")
}