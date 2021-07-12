output "LR_11_lambda_arn" {
  value = aws_lambda_function.LR-11-Lambda.arn
}

output "LR_11_lambda" {
  value = aws_lambda_function.LR-11-Lambda.id
}

output "region" {
  value = data.aws_region.current.name
}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}
