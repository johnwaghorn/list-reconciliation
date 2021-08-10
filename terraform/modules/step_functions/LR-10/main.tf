resource "aws_sfn_state_machine" "LR-10" {
  name     = var.name
  role_arn = aws_iam_role.role.arn

  definition = <<EOF
{
  "StartAt": "Demographic and registration outputs",
  "States": {
    "Demographic and registration outputs": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "Invoke LR15 Demo diffs lambda",
          "States": {
            "Invoke LR15 Demo diffs lambda": {
              "Type": "Task",
              "Resource": "${var.lr_15_lambda}",
              "InputPath": "$",
              "End": true
            }
          }
        },
        {
          "StartAt": "Registration outputs",
          "States": {
            "Registration outputs": {
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
      ],
      "Next": "Invoke LR14 send list rec results"
    },
    "Invoke LR14 send list rec results": {
      "Type": "Task",
      "Resource": "${var.lr_14_lambda}",
      "InputPath": "$",
      "End": true
    }
  }
}
EOF
}
