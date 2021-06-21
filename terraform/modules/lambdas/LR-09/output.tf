output "LR-09-lambda" {
  value = aws_lambda_function.LR-09-Lambda.arn
}

output "region" {
  value = data.aws_region.current.name
}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}
