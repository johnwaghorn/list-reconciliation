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
        "states.amazonaws.com",
      ]
    }
  }
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
    sid    = "CloudWatchAllow"
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction"
    ]

    resources = var.lambdas_to_invoke
  }
}
