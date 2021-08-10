variable "ssm_kms_arn" {
  type = string
}

variable "prefix" {
  type = string
}

variable "mesh_mappings" {
  description = "Mappings of MESH mailboxes"
  type = list(
    object({
      id = string
      outbound_mappings = list(object({
        dest_mailbox = string
        workflow_id  = string
      }))
    })
  )
  default = []

  validation {
    condition = alltrue([
      for mapping in var.mesh_mappings :
      can(regex("[0-9A-Za-z-]*", mapping.id))
    ])
    error_message = "The mapping names in mesh_mappings value must satisfy the regular expression [0-9A-Za-z-]*."
  }
}
