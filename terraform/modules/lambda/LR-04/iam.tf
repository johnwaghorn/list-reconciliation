locals {
  input_bucket_arn = var.source_bucket_arn
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
  description = "Policy for LR-04 ${var.lambda_name} Lambda Role."

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
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource":"${local.input_bucket_arn}/*"
        },
        {
            "Effect": "Allow",
            "Action": [
              "kms:Encrypt",
              "kms:Decrypt",
              "kms:ReEncrypt*",
              "kms:GenerateDataKey*"
            ],
            "Resource": [
                "${var.cloudwatch_kms_key.arn}",
                "${var.dynamodb_kms_key.arn}",
                "${var.s3_kms_key.arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:DescribeTable",
                "dynamodb:PutItem"
            ],
            "Resource": [
                "${var.errors_table_arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
              "kms:Encrypt",
              "kms:Decrypt",
              "kms:ReEncrypt*",
              "kms:GenerateDataKey*"
            ],
            "Resource": [
                "${var.cloudwatch_kms_key.arn}",
                "${var.dynamodb_kms_key.arn}",
                "${var.s3_kms_key.arn}"
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
