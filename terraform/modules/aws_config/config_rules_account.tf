resource "aws_config_config_rule" "account_part_of_organizations" {
  name = "account-part-of-organizations"

  source {
    owner             = "AWS"
    source_identifier = "ACCOUNT_PART_OF_ORGANIZATIONS"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "mfa_enabled_for_iam_console_access" {
  name = "mfa-enabled-for-iam-console-access"

  source {
    owner             = "AWS"
    source_identifier = "MFA_ENABLED_FOR_IAM_CONSOLE_ACCESS"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}
