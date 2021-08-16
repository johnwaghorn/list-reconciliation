import os

import boto3
import pytest
from freezegun import freeze_time

from lambda_code.LR_21_split_dps_extract.lr_21_lambda_handler import InvalidDSAFile
from utils.logger import success

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

MOCK_INPUT_BUCKET = os.environ.get("LR_20_SUPPLEMENTARY_INPUT_BUCKET")
MOCK_OUTPUT_BUCKET = os.environ.get("LR_22_SUPPLEMENTARY_OUTPUT_BUCKET")
REGION_NAME = os.environ.get("AWS_REGION")

VALID_DATA_FILE = "dps_data.csv"
INVALID_DATA_FILE = "invalid_dps_data.csv"
EXISTING_GP_FILE = "C86543.csv"


def test_lr_21_handler_expect_success(upload_valid_dps_data_to_s3, lambda_handler, lambda_context):
    event = {"Records": [{"s3": {"object": {"key": f"{VALID_DATA_FILE}"}}}]}

    response = lambda_handler.main(event, lambda_context)

    expected = "LR21 Lambda application stopped"

    assert response["message"] == expected


def test_lr_21_handler_invalid_event_fails(
    upload_valid_dps_data_to_s3, lambda_handler, lambda_context
):
    event = {"error": "error"}

    expected_response = "LR21 Lambda tried to access missing key='Records'"

    result = lambda_handler.main(event, lambda_context)

    assert expected_response in result["message"]


def test_split_dps_handler_expect_success(
    upload_valid_dps_data_to_s3, lambda_handler, lambda_context
):
    app = lambda_handler
    app.upload_key = VALID_DATA_FILE

    response = app.split_dps_extract()

    expected_response = "LR21 Lambda application stopped"

    assert response["message"] == expected_response

    # Test S3 file existence
    client = boto3.client("s3")
    paginator = client.get_paginator("list_objects_v2")

    pages = paginator.paginate(Bucket=MOCK_OUTPUT_BUCKET)

    actual = []

    for page in pages:
        for obj in page["Contents"]:
            actual.append(obj["Key"])

    expected = ["A76543.csv", "B85012.csv"]

    assert actual == expected

    # Test S3 file contents
    actual_file_1 = client.get_object(Bucket=MOCK_OUTPUT_BUCKET, Key=f"{expected[0]}")
    actual_file_1_contents = actual_file_1["Body"].read().decode("utf-8")

    expected_file_1_contents = "nhs_number,dispensing_flag\n1234567890,1\n1234567895,0"

    assert actual_file_1_contents == expected_file_1_contents

    actual_file_2 = client.get_object(Bucket=MOCK_OUTPUT_BUCKET, Key=f"{expected[1]}")
    actual_file_2_contents = actual_file_2["Body"].read().decode("utf-8")

    expected_file_2_contents = "nhs_number,dispensing_flag\n3234567891,1\n3234567892,0"

    assert actual_file_2_contents == expected_file_2_contents


@freeze_time("2021-06-29 14:01")
def test_cleanup_outdated_files_exceeds_minimum_date_expect_success(
    upload_existing_gp_data,
    upload_valid_dps_data_with_existing_gp_data,
    lambda_handler,
    lambda_context,
):
    app = lambda_handler
    app.upload_key = VALID_DATA_FILE

    # Test existing S3 files
    client = boto3.client("s3")
    paginator = client.get_paginator("list_objects_v2")

    pages = paginator.paginate(Bucket=MOCK_OUTPUT_BUCKET)

    outdated_gp_files = []

    for page in pages:
        for obj in page["Contents"]:
            outdated_gp_files.append(obj["Key"])

    assert EXISTING_GP_FILE in outdated_gp_files

    # Add new test data
    response = app.split_dps_extract()

    expected_response = "LR21 Lambda application stopped"

    assert response["message"] == expected_response

    # Test cleanup
    pages = paginator.paginate(Bucket=MOCK_OUTPUT_BUCKET)

    updated_gp_files = []

    for page in pages:
        for obj in page["Contents"]:
            updated_gp_files.append(obj["Key"])

    assert EXISTING_GP_FILE not in updated_gp_files


@freeze_time("2021-06-29 14:00")
def test_cleanup_outdated_files_within_minimum_date_expect_success(
    upload_existing_gp_data,
    upload_valid_dps_data_with_existing_gp_data,
    lambda_handler,
    lambda_context,
):
    app = lambda_handler
    app.upload_key = VALID_DATA_FILE

    # Test existing S3 files
    client = boto3.client("s3")
    paginator = client.get_paginator("list_objects_v2")

    pages = paginator.paginate(Bucket=MOCK_OUTPUT_BUCKET)

    outdated_gp_files = []

    for page in pages:
        for obj in page["Contents"]:
            outdated_gp_files.append(obj["Key"])

    assert EXISTING_GP_FILE in outdated_gp_files

    # Add new test data
    response = app.split_dps_extract()

    expected_response = "LR21 Lambda application stopped"

    assert response["message"] == expected_response

    # Test cleanup
    pages = paginator.paginate(Bucket=MOCK_OUTPUT_BUCKET)

    updated_gp_files = []

    for page in pages:
        for obj in page["Contents"]:
            updated_gp_files.append(obj["Key"])

    assert EXISTING_GP_FILE in updated_gp_files


def test_split_dps_extract_with_invalid_file_raises_invalid_error(
    upload_invalid_dps_data_to_s3,
    lambda_handler,
    lambda_context,
):
    app = lambda_handler
    app.upload_key = INVALID_DATA_FILE

    with pytest.raises(InvalidDSAFile):
        app.split_dps_extract()


def test_handler_with_invalid_file_raises_invalid_error(
    upload_invalid_dps_data_to_s3,
    lambda_handler,
    lambda_context,
):
    event = {"Records": [{"s3": {"object": {"key": f"{INVALID_DATA_FILE}"}}}]}

    result = lambda_handler.main(event, lambda_context)

    expected_response = (
        f'LR21 Lambda processed an invalid DSA file in uploadPath="{INVALID_DATA_FILE}"'
    )

    assert result["message"] == expected_response
