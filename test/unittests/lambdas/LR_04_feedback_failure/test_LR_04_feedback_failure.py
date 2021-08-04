import json
import os
import boto3

from freezegun import freeze_time

from services.jobs import get_job
from utils.datetimezone import get_datetime_now
from utils.database.models import Jobs
from utils.logger import success

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

MOCK_BUCKET = os.environ.get("AWS_S3_REGISTRATION_EXTRACT_BUCKET")
REGION_NAME = os.environ.get("AWS_REGION")

FAILED_FILE = "A12023_GPR4LNA1.CSB"
LOG_FILE = "A12023_GPR4LNA1.CSB_FailedFile_20200406144000.json"


def test_lr_04_handler_invalid_event_raises_key_error(
    upload_mock_data_to_s3, lambda_handler, lambda_context
):
    event = {"error": "error"}

    expected_response = "Lambda event has missing 'Records' key"

    result = lambda_handler.main(event, lambda_context)

    assert expected_response in result["message"]


@freeze_time("2020-04-06 13:40:00")
def test_lr04_lambda_handler_valid_file(
    upload_mock_data_to_s3, lr_04_event, lambda_context, lambda_handler
):
    app = lambda_handler

    result = app.main(event=lr_04_event, context=lambda_context)

    assert (
        f"Invalid file=fail/{FAILED_FILE} handled successfully from log={LOG_FILE}"
        in result["message"]
    )


@freeze_time("2020-04-06 13:40:00")
def test_lr04_lambda_handler_process_valid_log_successfully(
    upload_mock_data_to_s3, lr_04_event, lambda_context, lambda_handler
):
    app = lambda_handler

    result = app.main(event=lr_04_event, context=lambda_context)

    assert (
        f"Invalid file=fail/{FAILED_FILE} handled successfully from log={LOG_FILE}"
        in result["message"]
    )

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
