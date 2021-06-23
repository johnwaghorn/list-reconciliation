locals {
  patient_sqs_queue = "arn:aws:sqs:::${var.patient_sqs}"
}

resource "aws_iam_role" "role" {
  name        = "iam-role-${var.lambda_name}-${var.suffix}"
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
    name = "Lambda role for ${var.lambda_name} - ${var.suffix}"
  }
}

resource "aws_iam_policy" "policy" {
  name        = "iam-policy-${var.lambda_name}-${var.suffix}"
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
        },
        {
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": [
                "${var.mock_pds_data_bucket_arn}/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:DescribeTable",
            "Resource": [
                "${var.demographics_table_arn}",
                "${var.errors_table_arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:GetItem",
            "Resource": [
                "${var.demographics_table_arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:UpdateItem",
            "Resource": [
                "${var.demographics_table_arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:PutItem",
            "Resource": [
                "${var.errors_table_arn}"
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