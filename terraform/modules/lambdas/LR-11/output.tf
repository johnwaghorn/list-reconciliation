output "LR-11-lambda" {
  value = aws_lambda_function.LR-11-Lambda.arn
}

output "region" {
  value = data.aws_region.current.name
}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}
