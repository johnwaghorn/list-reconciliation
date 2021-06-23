resource "aws_sfn_state_machine" "LR-10" {
  name     = var.name
  role_arn = aws_iam_role.role.arn

  definition = <<EOF
{
  "StartAt": "Parallel",
  "States": {
    "Parallel": {
      "Type": "Parallel",
      "End": true,
      "Branches": [
        {
          "StartAt": "Invoke LR11 GP reg lambda",
          "States": {
            "Invoke LR11 GP reg lambda": {
              "Type": "Task",
              "Resource": "${var.lr_11_lambda}",
              "InputPath": "$",
              "End": true
            }
          }
        },
        {
          "StartAt": "Invoke LR12 PDS reg lambda",
          "States": {
            "Invoke LR12 PDS reg lambda": {
              "Type": "Task",
              "Resource": "${var.lr_12_lambda}",
              "InputPath": "$",
              "End": true
            }
          }
        }
      ]
    }
  }
}
EOF
}