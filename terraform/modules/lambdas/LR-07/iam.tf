locals {
  patient_sqs_queue = "arn:aws:sqs:::${var.patient_sqs}"
}

resource "aws_iam_role" "role" {
  name = "iam-role-${var.lambda_name}-${terraform.workspace}"
  description = "Execution Role for ${var.lambda_name} Lambda."

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF

  tags = {
    name = "Lambda role for ${var.lambda_name} - ${terraform.workspace}"
  }
}

resource "aws_iam_policy" "policy" {
  name = "iam-policy-${var.lambda_name}-${terraform.workspace}"
  description = "Policy for LR-07 ${var.lambda_name} Lambda Role."

  policy = <<-EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                 "sqs:ChangeMessageVisibility",
                 "sqs:DeleteMessage",
                 "sqs:GetQueueAttributes",
                 "sqs:ReceiveMessage"
            ],
            "Resource":"${var.patient_sqs_arn}"
        }
    ]
  }
  EOF
}

resource "aws_iam_role_policy_attachment" "policy_attachment" {
  role = aws_iam_role.role.name
  policy_arn = aws_iam_policy.policy.arn
}

