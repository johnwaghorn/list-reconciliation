resource "aws_config_config_rule" "kms_cmk_backing_key_rotation_enabled" {
  name = "kms-cmk-backing-key-rotation-enabled"

  source {
    owner             = "AWS"
    source_identifier = "CMK_BACKING_KEY_ROTATION_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "kms_cmk_not_scheduled_for_deletion" {
  name = "kms-cmk-not-scheduled-for-deletion"

  source {
    owner             = "AWS"
    source_identifier = "KMS_CMK_NOT_SCHEDULED_FOR_DELETION"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}
