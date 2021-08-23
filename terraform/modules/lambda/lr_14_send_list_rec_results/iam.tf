data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

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
    name = "Lambda role for LR-14-${var.suffix}"
  }
}

resource "aws_iam_policy" "policy" {
  name        = "iam-policy-${var.lambda_name}-${var.suffix}"
  description = "Policy for LR-14-${var.suffix} Lambda Role."
  policy      = <<EOF
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
                "s3:PutObject"
            ],
            "Resource": [
                "${var.mesh_send_bucket_arn}/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "${var.mesh_send_bucket_arn}",
                "${var.registrations_output_bucket_arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "${var.registrations_output_bucket_arn}/*"
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
                "${var.dynamodb_kms_key.arn}",
                "${var.s3_kms_key.arn}",
                "${var.mesh_kms_key.arn}",
                "${var.ssm_kms_key.arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:DescribeTable",
            "Resource": [
                "${var.demographics_differences_table_arn}",
                "${var.jobs_table_arn}",
                "${var.job_stats_table_arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:Query",
            "Resource": [
                "${var.demographics_differences_table_arn}",
                "${var.demographics_differences_table_arn}/index/*",
                "${var.jobs_table_arn}",
                "${var.jobs_table_arn}/index/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:GetItem",
            "Resource": [
                "${var.jobs_table_arn}",
                "${var.job_stats_table_arn}",
                "${var.demographics_differences_table_arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssm:GetParametersByPath",
                "ssm:GetParameters",
                "ssm:GetParameter"
            ],
            "Resource":[
                  "arn:aws:ssm:eu-west-2:${data.aws_caller_identity.current.account_id}:parameter/${var.mesh_ssm}/*",
                  "arn:aws:ssm:eu-west-2:${data.aws_caller_identity.current.account_id}:parameter/${var.email_ssm}/*"
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
