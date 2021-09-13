data "archive_file" "zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../build/${var.source_dir}"
  output_path = "${path.module}/../../../build/${var.source_dir}.zip"
}

resource "aws_lambda_layer_version" "layer" {
  filename            = data.archive_file.zip.output_path
  layer_name          = var.name
  compatible_runtimes = var.compatible_runtimes
  source_code_hash    = data.archive_file.zip.output_base64sha256
}
