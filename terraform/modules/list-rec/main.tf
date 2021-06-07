locals {
  lambda_name = {
    LR-02 = "LR_02_validate_and_parse"
    LR-07 = "LR_07_pds_hydrate"
    LR-08 = "LR_08_demographic_comparison"
  }
}

#---------------------Lambda Package layer ----------------
data "archive_file" "packages" {
  type        = "zip"
  source_dir  = "${path.module}/../../../lambda_layer"
  output_path = "${path.module}/../../../lambda_layer.zip"
}

resource "aws_lambda_layer_version" "package_layer" {
  filename            = data.archive_file.packages.output_path
  layer_name          = "lambda_layer_${terraform.workspace}"
  compatible_runtimes = [ "python3.8"]
  source_code_hash    = data.archive_file.packages.output_base64sha256
}

# -----------------------Lambda LR-02 ----------------------
module "LR-02" {
  source                = "../lambdas/LR-02"
  lambda_name           = local.lambda_name.LR-02
  package_layer_arn     = aws_lambda_layer_version.package_layer.arn
  runtime               = var.runtime
  source_bucket         = aws_s3_bucket.LR-01.bucket
  lr_01_inbound_folder  = aws_s3_bucket_object.inbound.key
  patient_sqs_arn       = aws_sqs_queue.Patient_Records_Queue.arn
}

# -----------------------Lambda LR-07----------------------
module "LR-07" {
  source            = "../lambdas/LR-07"
  lambda_name       = local.lambda_name.LR-07
  package_layer_arn = aws_lambda_layer_version.package_layer.arn
  runtime           = var.runtime
  lr_08_lambda      = module.LR-08.LR-08-lambda
  patient_sqs_arn   = aws_sqs_queue.Patient_Records_Queue.arn
}

# -----------------------Lambda LR-08----------------------
module "LR-08" {
  source            = "../lambdas/LR-08"
  lambda_name       = local.lambda_name.LR-08
  runtime           = var.runtime
  package_layer_arn = aws_lambda_layer_version.package_layer.arn
}

