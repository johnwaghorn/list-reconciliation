resource "aws_iam_role" "config" {
  name               = local.name
  description        = local.name
  assume_role_policy = data.aws_iam_policy_document.role_assume.json
}

data "aws_iam_policy_document" "role_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type = "Service"

      identifiers = [
        "config.amazonaws.com",
      ]
    }
  }
}

resource "aws_iam_role_policy_attachment" "policy_attachment" {
  role       = aws_iam_role.config.name
  policy_arn = aws_iam_policy.policy.arn
}

resource "aws_iam_policy" "policy" {
  name        = local.name
  description = local.name
  policy      = data.aws_iam_policy_document.policy.json
}

data "aws_iam_policy_document" "policy" {
  statement {
    sid    = "Allow"
    effect = "Allow"

    actions = []

    resources = []
  }
}
