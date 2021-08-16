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

data "aws_caller_identity" "current" {}

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
            "Action": "s3:GetObject",
            "Resource": [
                "${var.mock_pds_data_bucket_arn}/*"
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
                "${var.s3_kms_key.arn}",
                "${var.ssm_kms_key.arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:DescribeTable",
            "Resource": [
                "${var.demographics_table_arn}"
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
                "${var.demographics_table_arn}"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "${var.mock_pds_data_bucket_arn}/*"
        },
        {
            "Effect": "Allow",
            "Action": "lambda:InvokeFunction",
            "Resource": "${var.lr_08_lambda}"
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
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource":"${var.lr_06_bucket_arn}/*"
        },
         {
            "Effect": "Allow",
            "Action": [
                "ssm:PutParameter",
                "ssm:GetParametersByPath",
                "ssm:GetParameters",
                "ssm:GetParameter"
            ],
            "Resource":[
                  "arn:aws:ssm:eu-west-2:${data.aws_caller_identity.current.account_id}:parameter/${var.pds_ssm_prefix}/*"
           ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssm:PutParameter"
            ],
            "Resource":[
                  "${var.pds_ssm_access_token}"
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
