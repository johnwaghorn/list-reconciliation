import os

import boto3
import pytest
from freezegun import freeze_time
from lr_logging.exceptions import FeedbackLogError

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "..", "_data", "unit")

MOCK_BUCKET = os.environ.get("AWS_S3_REGISTRATION_EXTRACT_BUCKET")
REGION_NAME = os.environ.get("AWS_REGION")

JOB_ID = "50e1b957-2fc4-44b0-8e60-d8f9ca162099"
FAILED_FILE = "A12023_GPR4LNA1.CSB"
LOG_FILE = "A12023_GPR4LNA1.CSB-FailedFile-50e1b957-2fc4-44b0-8e60-d8f9ca162099.json"


def test_lr_04_handler_invalid_event_raises_key_error(
    upload_valid_log_to_s3, lambda_handler, lambda_context, ssm, email_ssm
):
    event = {"error": "error"}
    with pytest.raises(KeyError):
        lambda_handler.main(event, lambda_context)


@freeze_time("2020-04-06 13:40:00")
def test_lr04_lambda_handler_process_valid_log_successfully(
    upload_valid_log_to_s3, lr_04_event_valid_file, lambda_context, lambda_handler, ssm, email_ssm
):
    app = lambda_handler

    result = app.main(event=lr_04_event_valid_file, context=lambda_context)

    expected_subject = (
        "Validation Failure - PDS Comparison validation failure against 'A12023_GPR4LNA1.CSB'"
    )
    expected_body = (
        "The GP file: A12023_GPR4LNA1.CSB failed validation at 14:40:00 on 06/04/2020.\n"
        "As a result, no records in this file have been processed."
        "\n\nTotal records: 9"
        "\nTotal invalid records: 5"
        "\n\nThe reasons for the failure are:"
        "\nInvalid Record on lines 2-3"
        "\n   • GP Code - Must be a valid 7-digit numeric GMC National GP code and 1-6-digit alphanumeric Local GP code separated by a comma."
        "\n   • Destination HA Cipher - Must be a valid 3-digit alphanumeric code that matches the GP HA cipher"
        "\n   • Transaction/Record Date and Time - Must be a valid transmission date and timestamp, in the format YYYMMDDHHMM, which is less than 14 days old and not in the future."
        "\n   • Transaction/Record Number - Must be a unique, not-null integer greater than 0."
        "\nInvalid Record on lines 4-5"
        "\n   • Walking Units - Must be between 3 and 99 inclusive and be divisible by 3."
        "\nInvalid Record on lines 8-9"
        "\n   • Transaction/Record Number - Must be a unique, not-null integer greater than 0."
        "\n   • Walking Units - Must be between 3 and 99 inclusive and be divisible by 3."
        "\nInvalid Record on lines 14-15"
        "\n   • Blocked Route Special District Marker - Must be 'B' or 'S'."
        "\nInvalid Record on lines 18-19"
        "\n   • GP Code - Must be a valid 7-digit numeric GMC National GP code and 1-6-digit alphanumeric Local GP code separated by a comma."
        "\n   • Drug Dispensed Marker - Must be 'Y' or blank."
        "\n   • Blocked Route Special District Marker - Must be 'B' or 'S'."
        "\n\nPlease check and amend the file content and upload again.\n"
    )

    assert result["status"] == "success"
    assert result["message"] == f"LR04 Lambda application stopped for jobId='{JOB_ID}'"
    assert result["email_subject"] == expected_subject
    assert result["email_body"] == expected_body

    # Test file cleanup
    client = boto3.client("s3")

    response = client.list_objects_v2(Bucket=MOCK_BUCKET)

    deleted_key = f"fail/{FAILED_FILE}"
    log_key = f"fail/logs/{LOG_FILE}"

    existing_keys = []
    for existing in response.get("Contents", []):
        existing_keys.append(str(existing["Key"]))

    assert deleted_key not in existing_keys
    assert log_key in existing_keys


@freeze_time("2020-04-06 13:40:00")
def test_lr04_lambda_handler_process_invalid_log_successfully(
    upload_invalid_log_to_s3,
    lr_04_event_invalid_file,
    lambda_context,
    lambda_handler,
    ssm,
    email_ssm,
):
    app = lambda_handler

    with pytest.raises(FeedbackLogError):
        app.main(event=lr_04_event_invalid_file, context=lambda_context)
