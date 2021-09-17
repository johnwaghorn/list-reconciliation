resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.pds_api_mock_lambda_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.pds_api_mock.execution_arn}/*/*"
}

resource "aws_api_gateway_rest_api" "pds_api_mock" {
  name        = var.name
  description = var.name
  policy      = data.aws_iam_policy_document.policy.json

  endpoint_configuration {
    types            = ["PRIVATE"]
    vpc_endpoint_ids = [aws_vpc_endpoint.pds_api_mock.id]
  }
}

# Policy build by the AWS API Gateway Console
data "aws_iam_policy_document" "policy" {
  statement {
    sid       = ""
    effect    = "Deny"
    resources = ["execute-api:/*/*/*"]
    actions   = ["execute-api:Invoke"]

    condition {
      test     = "StringNotEquals"
      variable = "aws:sourceVpc"
      values   = [var.vpc_id]
    }

    principals {
      type        = "*"
      identifiers = ["*"]
    }
  }

  statement {
    sid       = ""
    effect    = "Allow"
    resources = ["execute-api:/*/*/*"]
    actions   = ["execute-api:Invoke"]

    principals {
      type        = "*"
      identifiers = ["*"]
    }
  }
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.pds_api_mock.id
  parent_id   = aws_api_gateway_rest_api.pds_api_mock.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.pds_api_mock.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id             = aws_api_gateway_rest_api.pds_api_mock.id
  resource_id             = aws_api_gateway_method.proxy.resource_id
  http_method             = aws_api_gateway_method.proxy.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.pds_api_mock_lambda_function.invoke_arn
}

resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = aws_api_gateway_rest_api.pds_api_mock.id
  resource_id   = aws_api_gateway_rest_api.pds_api_mock.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id             = aws_api_gateway_rest_api.pds_api_mock.id
  resource_id             = aws_api_gateway_method.proxy_root.resource_id
  http_method             = aws_api_gateway_method.proxy_root.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.pds_api_mock_lambda_function.invoke_arn
}

resource "aws_api_gateway_deployment" "pds_api_mock_deployment" {
  rest_api_id = aws_api_gateway_rest_api.pds_api_mock.id
  stage_name  = "api"

  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.lambda_root,
  ]
}
