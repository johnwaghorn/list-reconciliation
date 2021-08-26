resource "aws_sfn_state_machine" "step_function" {
  name       = "${var.environment}-${var.name}"
  role_arn   = aws_iam_role.role.arn
  definition = var.step_function_definition
}
