output "LR-11-sfn_arn" {
  value = aws_sfn_state_machine.LR-10.arn
}

output "LR-11-sfn" {
  value = aws_sfn_state_machine.LR-10.id
}
output "LR-10-step_function_arn" {
  value = aws_sfn_state_machine.LR-10.arn
}
