resource "aws_iam_role" "role" {
  name               = "iam-role-${var.lambda_name}-${var.suffix}"
  description        = "Execution Role for ${var.lambda_name} Lambda."
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
    name = "Lambda role for LR-09-${var.suffix}"
  }
}

resource "aws_iam_role_policy_attachment" "policy_attachment" {
  role       = aws_iam_role.role.name
  policy_arn = aws_iam_policy.policy.arn
}

resource "aws_iam_policy" "policy" {
  name        = "iam-policy-${var.lambda_name}-${var.suffix}"
  description = "Policy for LR-09-${var.suffix} Lambda Role."
  policy      = <<-EOF
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
            "Action": "dynamodb:DescribeTable",
            "Resource": [
                "${var.demographics_table_arn}",
                "${var.in_flight_table_arn}",
                "${var.jobs_table_arn}",
                "${var.job_stats_table_arn}",
                "${var.errors_table_arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:Scan",
            "Resource": [
                "${var.in_flight_table_arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:Query",
            "Resource": [
                "${var.demographics_table_arn}",
                "${var.demographics_table_arn}/index/*",
                "${var.jobs_table_arn}",
                "${var.jobs_table_arn}/index/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:UpdateItem",
            "Resource": [
                "${var.jobs_table_arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:DeleteItem",
            "Resource": [
                "${var.in_flight_table_arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:PutItem",
            "Resource": [
                "${var.errors_table_arn}",
                "${var.job_stats_table_arn}",
                "${var.jobs_table_arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "states:StartExecution",
            "Resource":"${var.lr_10_step_function_arn}"
        }
    ]
  }
  EOF
}
