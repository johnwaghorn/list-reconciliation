data "archive_file" "packages" {
  type        = "zip"
  source_dir  = "${path.module}/../../../packages_layer"
  output_path = "${path.module}/../../../packages_layer.zip"
}

resource "aws_lambda_layer_version" "packages_layer" {
  filename            = data.archive_file.packages.output_path
  layer_name          = "packages_layer_${var.suffix}"
  compatible_runtimes = ["python3.8"]
  source_code_hash    = data.archive_file.packages.output_base64sha256
}

data "archive_file" "dependencies" {
  type        = "zip"
  source_dir  = "${path.module}/../../../dependencies_layer"
  output_path = "${path.module}/../../../dependencies_layer.zip"
}

resource "aws_lambda_layer_version" "dependencies_layer" {
  filename            = data.archive_file.dependencies.output_path
  layer_name          = "dependencies_layer_${var.suffix}"
  compatible_runtimes = ["python3.8"]
  source_code_hash    = data.archive_file.dependencies.output_base64sha256
}
