data "archive_file" "packages" {
  type        = "zip"
  source_dir  = "${path.module}/../../../lambda_layer"
  output_path = "${path.module}/../../../lambda_layer.zip"
}

resource "aws_lambda_layer_version" "package_layer" {
  filename            = data.archive_file.packages.output_path
  layer_name          = "lambda_layer_${var.suffix}"
  compatible_runtimes = ["python3.8"]
  source_code_hash    = data.archive_file.packages.output_base64sha256
}
