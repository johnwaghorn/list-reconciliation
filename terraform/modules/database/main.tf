resource "aws_dynamodb_table" "tables" {
  hash_key  = var.table_hash_key
  name      = var.table_name
  range_key = var.table_range_key

  dynamic "attribute" {
    for_each = var.attributes
    content {
      name = attribute.value.name
      type = attribute.value.type
    }
  }

  billing_mode   = var.billing_mode
  stream_enabled = false

  dynamic "global_secondary_index" {
    for_each = var.secondary_index
    content {
      name            = global_secondary_index.value.name
      hash_key        = global_secondary_index.value.hash_key
      projection_type = global_secondary_index.value.projection_type
    }
  }
}