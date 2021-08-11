resource "aws_config_config_rule" "vpc_sg_open_only_to_authorized_ports" {
  name = "vpc-sg-open-only-to-authorized-ports"

  source {
    owner             = "AWS"
    source_identifier = "VPC_SG_OPEN_ONLY_TO_AUTHORIZED_PORTS"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "vpc_default_security_group_closed" {
  name = "vpc-default-security-group-closed"

  source {
    owner             = "AWS"
    source_identifier = "VPC_DEFAULT_SECURITY_GROUP_CLOSED"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}

resource "aws_config_config_rule" "vpc_restricted_common_ports" {
  name = "vpc-restricted-common-ports"

  source {
    owner             = "AWS"
    source_identifier = "RESTRICTED_COMMON_PORTS"
  }

  depends_on = [aws_config_configuration_recorder.nhsd_config]
}
