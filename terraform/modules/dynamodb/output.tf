output "dynamo_table_arn" {
  value = aws_dynamodb_table.tables.arn
}

output "dynamo_table_name" {
  value = aws_dynamodb_table.tables.name
}