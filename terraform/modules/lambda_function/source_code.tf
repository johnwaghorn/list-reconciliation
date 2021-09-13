data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../lambdas/${var.name}"
  output_path = "${path.module}/../../../build/${var.name}.zip"
}
