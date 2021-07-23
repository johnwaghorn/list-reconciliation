output "LR_04_lambda" {
  value = aws_lambda_function.LR-04-Lambda.id
}

output "LR-04-lambda_arn" {
  value = aws_lambda_function.LR-04-Lambda.arn
}

output "region" {
  value = data.aws_region.current.name
}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}