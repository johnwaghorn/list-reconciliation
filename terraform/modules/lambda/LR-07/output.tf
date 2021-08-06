output "pds_base_url_link" {
  value = var.pds_base_url
}

output "LR_07_lambda_arn" {
  value = aws_lambda_function.LR-07-Lambda.arn
}

output "LR_07_lambda" {
  value = aws_lambda_function.LR-07-Lambda.id
}
