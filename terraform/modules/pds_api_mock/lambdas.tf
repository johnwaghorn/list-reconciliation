data "archive_file" "archive" {
  type        = "zip"
  source_dir  = "${path.module}/../../../lambdas/pds_api_mock"
  output_path = "${path.module}/../../../lambdas/pds_api_mock.zip"
}

data "archive_file" "deps" {
  type        = "zip"
  source_dir  = "${path.module}/../../../pds_api_mock_deps"
  output_path = "${path.module}/../../../pds_api_mock_deps.zip"
}

resource "aws_lambda_layer_version" "package_layer" {
  filename            = data.archive_file.deps.output_path
  layer_name          = "pds_api_mock_${var.suffix}"
  compatible_runtimes = ["python3.8"]
  source_code_hash    = data.archive_file.deps.output_base64sha256
}

resource "aws_lambda_function" "pds_api_mock" {
  function_name    = "pds-api-mock-${var.suffix}"
  description      = "pds-api-mock-${var.suffix}"
  handler          = "app.main.handler"
  runtime          = var.runtime
  layers           = [aws_lambda_layer_version.package_layer.arn]
  role             = aws_iam_role.lambda_exec_role.arn
  memory_size      = 128
  timeout          = 300
  source_code_hash = data.archive_file.archive.output_base64sha256
  filename         = data.archive_file.archive.output_path

  environment {
    variables = {
      PDS_BUCKET    = var.fhir_data_bucket
      PDS_DATA_FILE = var.fhir_data_file
    }
  }
}

resource "aws_lambda_permission" "apigw_lambda_perm" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pds_api_mock.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.pds_api_mock.execution_arn}/*/*"
}
