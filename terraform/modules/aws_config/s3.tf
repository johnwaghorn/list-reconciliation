resource "aws_s3_bucket" "config" {
  bucket = local.name
  acl    = "private"
}
