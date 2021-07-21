output "LR-24-lambda_arn" {
  value = aws_lambda_function.LR-24-lambda.arn
}

output "LR-24-lambda" {
  value = aws_lambda_function.LR-24-lambda.id
}

output "region" {
  value = data.aws_region.current.name
}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}
