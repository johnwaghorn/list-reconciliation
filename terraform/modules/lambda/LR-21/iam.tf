locals {
  supplementary-input-bucket  = "arn:aws:s3:::${var.supplementary-input-bucket}"
  supplementary-output-bucket = "arn:aws:s3:::${var.supplementary-output-bucket}"
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

resource "aws_iam_role" "role" {
  name               = "iam-role-${var.lambda_name}-${var.suffix}"
  description        = "Execution Role for ${var.lambda_name} Lambda."
  assume_role_policy = <<-EOF
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
    name = "Lambda role for ${var.lambda_name} - ${var.suffix}"
  }
}

resource "aws_iam_policy" "policy" {
  name        = "iam-policy-${var.lambda_name}-${var.suffix}"
  description = "Policy for LR-21 ${var.lambda_name} Lambda Role."

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
                "s3:ListBucket"
            ],
            "Resource":[
              "${local.supplementary-input-bucket}",
              "${local.supplementary-output-bucket}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource":[
              "${local.supplementary-input-bucket}/*",
              "${local.supplementary-output-bucket}/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
              "dynamodb:DescribeTable",
              "dynamodb:PutItem"
            ],
            "Resource": "${var.errors_table_arn}"
        }
    ]
  }
  EOF

}

resource "aws_iam_role_policy_attachment" "policy_attachment" {
  role       = aws_iam_role.role.name
  policy_arn = aws_iam_policy.policy.arn
}