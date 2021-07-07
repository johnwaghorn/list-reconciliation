import os

import boto3
import pytest


import boto3
from freezegun import freeze_time

from lambda_code.LR_02_validate_and_parse.lr_02_functions import ValidateAndParse


from utils.database.models import Demographics, Jobs, InFlight


from utils.logger import success

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

MOCK_BUCKET = os.environ.get("AWS_S3_REGISTRATION_EXTRACT_BUCKET")
MOCK_QUEUE = os.environ.get("AWS_PATIENT_RECORD_SQS")
REGION_NAME = os.environ.get("AWS_REGION")

JOB_ID = "50e1b957-2fc4-44b0-8e60-d8f9ca162099"

VALID_FILE = "GPR4LNA1.CSA"
INVALID_FILE = "GPR4LNA1.CSB"


def test_lr_02_handler_invalid_event_raises_key_error(
    upload_pds_valid_mock_data_to_s3, lambda_handler, lambda_context
):
    event = {"error": "error"}
    expected_response = "Lambda event has missing 'Records' key"
    result = lambda_handler.main(event, lambda_context)
    assert expected_response in result["message"]


@freeze_time("2020-04-06 13:40:00")
def test_lr02_lambda_handler(
    upload_pds_valid_mock_data_to_s3,
    create_dynamodb_tables,
    create_sqs,
    lr_02_event,
    lambda_context,
    lambda_handler,
    monkeypatch,
):

    env = os.environ.copy()
    result = lambda_handler.main(event=lr_02_event, context=lambda_context)

    assert f"{VALID_FILE} processed successfully for Job" in result["message"]


@freeze_time("2020-04-06 13:40:00")
def test_validate_and_process_with_invalid_upload_handles_correctly(
    upload_pds_invalid_mock_data_to_s3, create_dynamodb_tables, lambda_handler
):
    upload_key = f"inbound/{INVALID_FILE}"

    env = os.environ.copy()
    logger = lambda_handler.log_object

    lr02 = ValidateAndParse(upload_key, JOB_ID, env, logger)

    response = lr02.validate_and_process_extract()

    expected = success(
        f"Invalid file {INVALID_FILE} handled successfully for Job: {JOB_ID}"
    )

    assert response == expected

    # Test S3 validity
    with open(os.path.join(DATA, f"{INVALID_FILE}")) as f:
        expected_file_contents = f.read()

    s3_client = boto3.client("s3")

    actual_file = s3_client.get_object(Bucket=MOCK_BUCKET, Key=f"fail/{INVALID_FILE}")
    actual_file_contents = actual_file["Body"].read().decode("utf-8")

    assert expected_file_contents == actual_file_contents
