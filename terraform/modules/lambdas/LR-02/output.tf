output "LR_02_lambda" {
  value = aws_lambda_function.LR-02-Lambda.id
}

output "LR-02-lambda_arn" {
  value = aws_lambda_function.LR-02-Lambda.arn
}

output "region" {
  value = data.aws_region.current.name
}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}