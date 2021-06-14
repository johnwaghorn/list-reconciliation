resource "aws_iam_role" "role" {
  name                = "iam-role-${var.name}"
  description         = "Execution Role for ${var.name} Step function."
  assume_role_policy  = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "states.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF

  tags = {
    name = "Lambda role for ${var.name}"
  }
}

resource "aws_iam_policy" "policy" {
  name        = "iam-policy-${var.name}"
  description = "Policy for LR-10 ${var.name} Step function Role."
  policy      = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": [
                "${var.lr_11_lambda}",
                "${var.lr_11_lambda}:*"
            ]
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "policy_attachment" {
  role       = aws_iam_role.role.name
  policy_arn = aws_iam_policy.policy.arn
}

