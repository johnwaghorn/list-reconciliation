
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
        "logs.${data.aws_region.current.name}.amazonaws.com",
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
  # TODO restrict
  statement {
    sid    = "FirehoseAllow"
    effect = "Allow"

    actions = [
      "firehose:*"
    ]

    resources = [
      "${var.firehose_stream_arn}"
    ]
  }

  statement {
    sid    = "IAMAllow"
    effect = "Allow"

    actions = [
      "iam:PassRole"
    ]

    resources = [
      "${aws_iam_role.role.arn}"
    ]
  }
}
