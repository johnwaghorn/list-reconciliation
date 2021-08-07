resource "aws_iam_role" "role" {
  name               = "${local.name}-role"
  description        = "${local.name}-role"
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
  name        = "${local.name}-policy"
  description = "${local.name}-policy"
  policy      = data.aws_iam_policy_document.policy.json
}

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
    sid    = "KMSLRAllow"
    effect = "Allow"

    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*"
    ]

    resources = [
      var.cloudwatch_kms_key.arn,
      var.s3_kms_key.arn
    ]
  }

  statement {
    sid    = "S3List"
    effect = "Allow"

    actions = [
      "s3:ListBucket"
    ]

    resources = [
      var.supplementary_input_bucket_arn,
      var.supplementary_output_bucket_arn
    ]
  }

  statement {
    sid    = "S3Allow"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]

    resources = [
      "${var.supplementary_input_bucket_arn}/*",
      "${var.supplementary_output_bucket_arn}/*"
    ]
  }

  statement {
    sid    = "LambdaAllow"
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction",
    ]

    resources = [
      aws_lambda_function.lambda.arn,
      "${aws_lambda_function.lambda.arn}:*"
    ]
  }
}
