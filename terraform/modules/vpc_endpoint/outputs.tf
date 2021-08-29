output "endpoint" {
  value = aws_vpc_endpoint.endpoint
}

output "security_group" {
  value = try(aws_security_group.endpoint[0], null)
}
