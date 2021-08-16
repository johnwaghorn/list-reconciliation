resource "aws_iam_role" "role" {
  name               = "iam-role-${local.name}"
  description        = "Execution Role for ${var.lambda_name} Lambda"
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
  description = "Policy for LR-21 ${var.lambda_name} Lambda Role."
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

  dynamic "statement" {
    # If we have a Mesh KMS Key Alias, create this statement
    # (count is not supported here, so we use for_each)
    for_each = var.mesh_kms_key_alias != "" ? [var.mesh_kms_key_alias] : []

    content {
      sid    = "KMSAllow"
      effect = "Allow"

      actions = [
        "kms:decrypt",
      ]

      resources = [
        data.aws_kms_alias.mesh[0].target_key_arn
      ]
    }
  }

  dynamic "statement" {
    for_each = var.mesh_post_office_mappings

    content {
      sid    = "S3List${statement.value.name}"
      effect = "Allow"

      actions = [
        "s3:ListBucket",
      ]

      resources = [
        "arn:aws:s3:::${statement.value.inbound.bucket}",
        "arn:aws:s3:::${statement.value.outbound.bucket}"
      ]
    }
  }

  dynamic "statement" {
    for_each = var.mesh_post_office_mappings

    content {
      sid    = "S3Inbound${statement.value.name}"
      effect = "Allow"

      actions = [
        "s3:GetObjectTagging",
        "s3:GetObject",
        "s3:DeleteObject"
      ]

      resources = [
        "arn:aws:s3:::${statement.value.inbound.bucket}/${statement.value.inbound.key}*"
      ]
    }
  }

  dynamic "statement" {
    for_each = var.mesh_post_office_mappings

    content {
      sid    = "S3Outbound${statement.value.name}"
      effect = "Allow"

      actions = [
        "s3:PutObject*",
      ]

      resources = [
        "arn:aws:s3:::${statement.value.outbound.bucket}/${statement.value.outbound.key}*"
      ]
    }
  }

  statement {
    sid    = "SSMAllow"
    effect = "Allow"

    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath"
    ]

    resources = [
      "arn:aws:ssm:eu-west-2:${data.aws_caller_identity.current.account_id}:parameter/${local.name}*"
    ]
  }
}
