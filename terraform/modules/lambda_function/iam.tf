resource "aws_iam_role" "role" {
  name               = "${var.environment}-${var.name}-role"
  description        = "${var.environment}-${var.name}-role"
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

resource "aws_iam_role_policy_attachment" "policy_vpc_attachment" {
  role       = aws_iam_role.role.name
  policy_arn = data.aws_iam_policy.policy_vpc.arn
}

data "aws_iam_policy" "policy_vpc" {
  name = "AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "policy_attachment" {
  role       = aws_iam_role.role.name
  policy_arn = aws_iam_policy.policy.arn
}

resource "aws_iam_policy" "policy" {
  name        = "${var.environment}-${var.name}-policy"
  description = "${var.environment}-${var.name}-policy"
  policy      = data.aws_iam_policy_document.policy.json
}

#tfsec:ignore:aws-iam-no-policy-wildcards
data "aws_iam_policy_document" "policy" {
  statement {
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

  dynamic "statement" {
    for_each = length(var.dynamodb_read_only) > 0 ? ["DynamoDBReadOnly"] : []

    content {
      effect = "Allow"

      actions = [
        "dynamodb:DescribeTable",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
      ]

      resources = var.dynamodb_read_only
    }
  }

  dynamic "statement" {
    for_each = length(var.dynamodb_read_write) > 0 ? ["DynamoDBReadWrite"] : []

    content {
      effect = "Allow"

      actions = [
        "dynamodb:BatchWriteItem",
        "dynamodb:DeleteItem",
        "dynamodb:DescribeTable",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem",
      ]

      resources = var.dynamodb_read_write
    }
  }

  dynamic "statement" {
    for_each = length(var.kms_read_only) > 0 ? ["KMSReadOnly"] : []

    content {
      effect = "Allow"

      actions = [
        "kms:Decrypt",
      ]

      resources = var.kms_read_only
    }
  }

  dynamic "statement" {
    for_each = length(var.kms_read_write) > 0 ? ["KMSReadWrite"] : []

    content {
      effect = "Allow"

      actions = [
        "kms:Decrypt",
        "kms:Encrypt",
        "kms:GenerateDataKey*",
        "kms:ReEncrypt*",
      ]

      resources = var.kms_read_write
    }
  }

  dynamic "statement" {
    for_each = length(var.lambdas_to_invoke) > 0 || var.lambda_invoke_self ? ["LambdaInvoke"] : []

    content {
      effect = "Allow"

      actions = [
        "lambda:InvokeFunction",
      ]

      resources = var.lambda_invoke_self ? concat(var.lambdas_to_invoke, [aws_lambda_function.lambda.arn]) : var.lambdas_to_invoke
      # TODO support <lambda_arn>:* ?
      # resources = [join(":", [statement.value, "*"])]
    }
  }

  dynamic "statement" {
    for_each = length(flatten([var.s3_read_write, var.s3_read_only])) > 0 ? ["S3List"] : []

    content {
      effect = "Allow"

      actions = [
        "s3:ListBucket",
      ]

      resources = flatten([var.s3_read_write, var.s3_read_only])
    }
  }

  dynamic "statement" {
    for_each = length(var.ssm_read_only) > 0 ? ["SSMReadOnly"] : []

    content {
      effect = "Allow"

      actions = [
        "ssm:GetParameter",
      ]

      resources = var.ssm_read_only
    }
  }

  dynamic "statement" {
    for_each = length(var.ssm_read_by_path) > 0 ? ["SSMReadByPath"] : []

    content {
      effect = "Allow"

      actions = [
        "ssm:GetParameters",
        "ssm:GetParametersByPath",
      ]

      resources = var.ssm_read_by_path
    }
  }

  dynamic "statement" {
    for_each = length(var.ssm_read_write) > 0 ? ["SSMReadWrite"] : []

    content {
      effect = "Allow"

      actions = [
        "ssm:GetParameter",
        "ssm:PutParameter"
      ]

      resources = var.ssm_read_write
    }
  }

  dynamic "statement" {
    for_each = length(var.step_functions_to_invoke) > 0 ? ["StepFunctionInvoke"] : []

    content {
      effect = "Allow"

      actions = [
        "states:StartExecution"
      ]

      resources = var.step_functions_to_invoke
    }
  }

  dynamic "statement" {
    for_each = length(var.s3_read_only) > 0 ? var.s3_read_only : []

    content {
      effect = "Allow"

      actions = [
        "s3:GetObject",
        "s3:GetObjectTagging",
      ]

      resources = [join("/", [statement.value, "*"])]
    }
  }

  dynamic "statement" {
    for_each = length(var.s3_read_write) > 0 ? var.s3_read_write : []

    content {
      effect = "Allow"

      actions = [
        "s3:DeleteObject",
        "s3:GetObject",
        "s3:GetObjectTagging",
        "s3:PutObject",
      ]

      resources = [join("/", [statement.value, "*"])]
    }
  }
}
