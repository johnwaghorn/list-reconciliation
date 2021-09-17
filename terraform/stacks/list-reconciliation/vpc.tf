data "aws_vpc" "account" {
  filter {
    name   = "tag:Name"
    values = [try(local.shared_vpc_name[local.environment], local.shared_vpc_name["default"])]
  }
}

data "aws_subnet_ids" "intra" {
  vpc_id = data.aws_vpc.account.id
  filter {
    name   = "tag:Name"
    values = ["dev-vpc-intra-eu-west-2a", "dev-vpc-intra-eu-west-2b", "dev-vpc-intra-eu-west-2c"] # TODO build list
  }
}

data "aws_subnet_ids" "private" {
  vpc_id = data.aws_vpc.account.id
  filter {
    name   = "tag:Name"
    values = ["dev-vpc-private-eu-west-2a", "dev-vpc-private-eu-west-2b", "dev-vpc-private-eu-west-2c"] # TODO build list
  }
}

data "aws_subnet_ids" "public" {
  vpc_id = data.aws_vpc.account.id
  filter {
    name   = "tag:Name"
    values = ["dev-vpc-public-eu-west-2a", "dev-vpc-public-eu-west-2b", "dev-vpc-public-eu-west-2c"] # TODO build list
  }
}

data "aws_vpc_endpoint" "s3" {
  vpc_id       = data.aws_vpc.account.id
  service_name = "com.amazonaws.eu-west-2.s3"
}

data "aws_vpc_endpoint" "dynamodb" {
  vpc_id       = data.aws_vpc.account.id
  service_name = "com.amazonaws.eu-west-2.dynamodb"
}

data "aws_vpc_endpoint" "cloudwatch" {
  vpc_id       = data.aws_vpc.account.id
  service_name = "com.amazonaws.eu-west-2.logs"
}

data "aws_vpc_endpoint" "kms" {
  vpc_id       = data.aws_vpc.account.id
  service_name = "com.amazonaws.eu-west-2.kms"
}

data "aws_vpc_endpoint" "ssm" {
  vpc_id       = data.aws_vpc.account.id
  service_name = "com.amazonaws.eu-west-2.ssm"
}

data "aws_vpc_endpoint" "lambda" {
  vpc_id       = data.aws_vpc.account.id
  service_name = "com.amazonaws.eu-west-2.lambda"
}

data "aws_vpc_endpoint" "step_function" {
  vpc_id       = data.aws_vpc.account.id
  service_name = "com.amazonaws.eu-west-2.states"
}
