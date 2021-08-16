import os
import boto3

from freezegun import freeze_time

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

MOCK_BUCKET = os.environ.get("AWS_S3_REGISTRATION_EXTRACT_BUCKET")
REGION_NAME = os.environ.get("AWS_REGION")

FAILED_FILE = "A12023_GPR4LNA1.CSB"
LOG_FILE = "A12023_GPR4LNA1.CSB-FailedFile-50e1b957-2fc4-44b0-8e60-d8f9ca162099.json"


def test_lr_04_handler_invalid_event_raises_key_error(
    upload_mock_data_to_s3, lambda_handler, lambda_context
):
    event = {"error": "error"}

    expected_response = "LR04 Lambda tried to access missing key='Records'"

    result = lambda_handler.main(event, lambda_context)

    assert expected_response in result["message"]


@freeze_time("2020-04-06 13:40:00")
def test_lr04_lambda_handler_valid_file(
    upload_mock_data_to_s3, lr_04_event, lambda_context, lambda_handler
):
    app = lambda_handler

    result = app.main(event=lr_04_event, context=lambda_context)

    expected = "LR04 Lambda application stopped"

    assert result["message"] == expected


@freeze_time("2020-04-06 13:40:00")
def test_lr04_lambda_handler_process_valid_log_successfully(
    upload_mock_data_to_s3, lr_04_event, lambda_context, lambda_handler
):
    app = lambda_handler

    result = app.main(event=lr_04_event, context=lambda_context)

    expected = "LR04 Lambda application stopped"

    assert result["message"] == expected

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
