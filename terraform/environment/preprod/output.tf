output "lr_01_bucket" {
  value = module.List-Recon.LR_01_Bucket
}

output "lr_01_bucket_inbound" {
  value = module.List-Recon.LR_01_Bucket_inbound
}

output "lr_01_bucket_pass" {
  value = module.List-Recon.LR_01_Bucket_pass
}

output "lr_01_bucket_fail" {
  value = module.List-Recon.LR_01_Bucket_fail
}

output "lr_01_bucket_retry" {
  value = module.List-Recon.LR_01_Bucket_retry
}

output "patients_queue" {
  value = module.List-Recon.sqs_queue_name
}