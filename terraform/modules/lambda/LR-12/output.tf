output "LR-12-lambda_arn" {
  value = aws_lambda_function.LR-12-Lambda.arn
}

output "LR-12-lambda" {
  value = aws_lambda_function.LR-12-Lambda.id
}

output "region" {
  value = data.aws_region.current.name
}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}
