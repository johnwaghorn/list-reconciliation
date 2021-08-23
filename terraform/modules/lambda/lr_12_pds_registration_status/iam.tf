resource "aws_iam_role" "role" {
  name               = "iam-role-${local.name}"
  description        = "iam-role-${local.name}"
  assume_role_policy = data.aws_iam_policy_document.role_assume.json
}

data "aws_iam_policy_document" "role_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"

      identifiers = [
        "lambda.amazonaws.com",
      ]
    }
  }
}

resource "aws_iam_role_policy_attachment" "policy_attachment" {
  role       = aws_iam_role.role.name
  policy_arn = aws_iam_policy.policy.arn
}

resource "aws_iam_policy" "policy" {
  name        = "iam-policy-${local.name}"
  description = "iam-policy-${local.name}"
  policy      = data.aws_iam_policy_document.policy.json
}

#tfsec:ignore:aws-iam-no-policy-wildcards
data "aws_iam_policy_document" "policy" {
  statement {
    sid    = "CloudWatchAllow"
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      aws_cloudwatch_log_group.lambda.arn,
      "${aws_cloudwatch_log_group.lambda.arn}:*"
    ]
  }

  statement {
    sid    = "S3Write"
    effect = "Allow"

    actions = [
      "s3:PutObject",
      "s3:DeleteObject",
    ]

    resources = [
      "${var.registrations_output_bucket_arn}/*"
    ]
  }

  statement {
    sid    = "S3Read"
    effect = "Allow"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${var.pds_practice_registrations_bucket_arn}/*"
    ]
  }

  statement {
    sid    = "KMSAllow"
    effect = "Allow"

    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
    ]

    resources = [
      var.cloudwatch_kms_key.arn,
      var.dynamodb_kms_key.arn,
      var.s3_kms_key.arn,
      var.ssm_kms_key.arn,
    ]
  }

  statement {
    sid    = "DynamoDescribe"
    effect = "Allow"

    actions = [
      "dynamodb:DescribeTable"
    ]

    resources = [
      var.demographics_table_arn,
      var.jobs_table_arn,
      var.job_stats_table_arn,
    ]
  }

  statement {
    sid    = "DynamoQuery"
    effect = "Allow"

    actions = [
      "dynamodb:Query"
    ]

    resources = [
      var.demographics_table_arn,
      "${var.demographics_table_arn}/index/*",
      var.jobs_table_arn,
      "${var.jobs_table_arn}/index/*",
    ]
  }

  statement {
    sid    = "DynamoWrite"
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:PutItem"
    ]

    resources = [
      var.job_stats_table_arn
    ]
  }

  statement {
    sid    = "SSMAllow"
    effect = "Allow"

    actions = [
      "ssm:GetParametersByPath",
      "ssm:GetParameters",
      "ssm:GetParameter",
    ]

    resources = [
      "arn:aws:ssm:eu-west-2:${data.aws_caller_identity.current.account_id}:parameter/${var.pds_ssm_prefix}/*"
    ]
  }

  statement {
    sid    = "SSMWrite"
    effect = "Allow"

    actions = [
      "ssm:PutParameter"
    ]

    resources = [
      var.pds_ssm_access_token
    ]
  }
}
