resource "aws_config_config_rule" "iam_policy_no_statements_with_admin_access" {
  name = "iam-policy-no-statements-with-admin-access"

  source {
    owner             = "AWS"
    source_identifier = "IAM_POLICY_NO_STATEMENTS_WITH_ADMIN_ACCESS"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "iam_access_keys_rotated" {
  name             = "iam-access-keys-rotated"
  input_parameters = jsonencode({ "maxAccessKeyAge" = "90" })

  source {
    owner             = "AWS"
    source_identifier = "ACCESS_KEYS_ROTATED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "iam_user_unused_credentials_check" {
  name             = "iam-user-unused-credentials-check"
  input_parameters = jsonencode({ "maxCredentialUsageAge" = "90" })

  source {
    owner             = "AWS"
    source_identifier = "IAM_USER_UNUSED_CREDENTIALS_CHECK"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "iam_user_mfa_enabled" {
  name = "iam-user-mfa-enabled"

  source {
    owner             = "AWS"
    source_identifier = "IAM_USER_MFA_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "iam_mfa_enabled_for_iam_console_access" {
  name = "iam-mfa-enabled-for-iam-console-access"

  source {
    owner             = "AWS"
    source_identifier = "MFA_ENABLED_FOR_IAM_CONSOLE_ACCESS"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}
