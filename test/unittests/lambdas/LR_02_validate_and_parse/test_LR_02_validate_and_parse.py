import json
import os
import boto3

from freezegun import freeze_time

from utils.datetimezone import get_datetime_now
from utils.database.models import Jobs, InFlight
from utils.logger import success

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

MOCK_BUCKET = os.environ.get("AWS_S3_REGISTRATION_EXTRACT_BUCKET")
MOCK_QUEUE = os.environ.get("AWS_PATIENT_RECORD_SQS")
REGION_NAME = os.environ.get("AWS_REGION")

JOB_ID = "50e1b957-2fc4-44b0-8e60-d8f9ca162099"

VALID_FILE = "A82023_GPR4LNA1.CSA"
INVALID_FILE = "A12023_GPR4LNA1.CSB"


def test_lr_02_handler_invalid_event_raises_key_error(
    upload_valid_mock_data_to_s3, lambda_handler, lambda_context
):
    event = {"error": "error"}

    expected_response = "Lambda event has missing 'Records' key"

    result = lambda_handler.main(event, lambda_context)

    assert expected_response in result["message"]


@freeze_time("2020-04-06 13:40:00")
def test_lr02_lambda_handler_valid_file(
    upload_valid_mock_data_to_s3,
    create_dynamodb_tables,
    create_LR24_lambda,
    lr_02_valid_file_event,
    lambda_context,
    lambda_handler,
):
    app = lambda_handler

    result = app.main(event=lr_02_valid_file_event, context=lambda_context)

    assert f"{VALID_FILE} processed successfully for Job" in result["message"]


@freeze_time("2020-04-06 13:40:00")
def test_lr02_lambda_handler_invalid_file(
    upload_invalid_mock_data_to_s3,
    create_dynamodb_tables,
    create_LR24_lambda,
    lr_02_invalid_file_event,
    lambda_context,
    lambda_handler,
):
    app = lambda_handler

    result = app.main(event=lr_02_invalid_file_event, context=lambda_context)

    assert f"{INVALID_FILE} handled successfully for Job" in result["message"]


@freeze_time("2020-04-06 13:40:00")
def test_validate_and_process_with_valid_upload_handles_correctly(
    upload_valid_mock_data_to_s3,
    create_dynamodb_tables,
    create_LR24_lambda,
    lr_02_valid_file_event,
    lambda_context,
    lambda_handler,
):
    app = lambda_handler
    app.job_id = JOB_ID
    app.upload_key = f"inbound/{VALID_FILE}"
    app.upload_filename = VALID_FILE

    response = app.validate_and_process_extract()

    expected = success(f"{VALID_FILE} processed successfully for Job: {JOB_ID}")

    assert response == expected

    # Test Job validity
    expected_job = Jobs(
        JOB_ID,
        PracticeCode="A82023",
        FileName=VALID_FILE,
        Timestamp=get_datetime_now(),
        StatusId="1",
    )
    expected_job_attributes = expected_job.attribute_values

    actual_job = Jobs.get(JOB_ID, "A82023")
    actual_job_attributes = actual_job.attribute_values
    assert expected_job_attributes == actual_job_attributes

    # Test InFlight validity
    expected_inflight = InFlight(JOB_ID, TotalRecords=1)
    actual_inflight = InFlight.get(JOB_ID)
    assert expected_inflight.JobId == actual_inflight.JobId
    assert expected_inflight.TotalRecords == actual_inflight.TotalRecords

    # Test S3 validity
    with open(os.path.join(DATA, f"{VALID_FILE}")) as f:
        expected_file_contents = f.read()

    s3_client = boto3.client("s3")

    actual_file = s3_client.get_object(Bucket=MOCK_BUCKET, Key=f"pass/{VALID_FILE}")
    actual_file_contents = actual_file["Body"].read().decode("utf-8")

    assert expected_file_contents == actual_file_contents


@freeze_time("2020-04-06 13:40:00")
def test_validate_and_process_with_invalid_upload_handles_correctly(
    upload_invalid_mock_data_to_s3,
    create_dynamodb_tables,
    lr_02_invalid_file_event,
    lambda_handler,
):
    app = lambda_handler
    app.job_id = JOB_ID
    app.upload_key = f"inbound/{INVALID_FILE}"
    app.upload_filename = INVALID_FILE

    response = app.validate_and_process_extract()

    expected = success(f"Invalid file {INVALID_FILE} handled successfully for Job: {JOB_ID}")

    assert response == expected

    # Test S3 validity
    with open(os.path.join(DATA, f"{INVALID_FILE}")) as f:
        expected_file_contents = f.read()

    s3_client = boto3.client("s3")

    actual_file = s3_client.get_object(Bucket=MOCK_BUCKET, Key=f"fail/{INVALID_FILE}")
    actual_file_contents = actual_file["Body"].read().decode("utf-8")

    assert expected_file_contents == actual_file_contents

    # Test log validity
    expected_log = {
        "file": INVALID_FILE,
        "upload_date": "2020-04-06 13:40:00+00:00",
        "error_type": "INVALID_STRUCTURE",
        "message": [r"Header must be 503\*"],
    }

    expected_log_key = "fail/logs/A12023_GPR4LNA1.CSB_FailedFile_20200406134000.json"
    actual_log_key = (
        f"fail/logs/{INVALID_FILE}_FailedFile_{get_datetime_now().strftime('%Y%m%d%H%M%S')}.json"
    )

    assert expected_log_key == actual_log_key

    actual_log_file = s3_client.get_object(Bucket=MOCK_BUCKET, Key=actual_log_key)
    actual_log_contents = actual_log_file["Body"].read().decode("utf-8")

    assert expected_log == json.loads(actual_log_contents)
