import os

import boto3
import pytest
from freezegun import freeze_time
from moto import mock_dynamodb2, mock_s3

from lambda_code.LR_21_split_dps_extract.lr_21_lambda_handler import SplitDPSExtract
from utils.database.models import Errors


ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

MOCK_INPUT_BUCKET = os.environ.get("LR_20_SUPPLEMENTARY_INPUT_BUCKET")
MOCK_OUTPUT_BUCKET = os.environ.get("LR_22_SUPPLEMENTARY_OUTPUT_BUCKET")
REGION_NAME = os.environ.get("AWS_REGION")

VALID_DATA_FILE = "dps_data.csv"
INVALID_DATA_FILE = "invalid_dps_data.csv"
EXISTING_GP_FILE = "C86543.csv"


@pytest.fixture(scope="module")
def lambda_handler():
    app = SplitDPSExtract()
    return app


@pytest.fixture
def upload_valid_dps_data_to_s3():
    with mock_s3():
        client = boto3.client("s3", region_name=REGION_NAME)
        client.create_bucket(
            Bucket=MOCK_INPUT_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
        )
        client.create_bucket(
            Bucket=MOCK_OUTPUT_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
        )
        client.upload_file(
            os.path.join(DATA, f"{VALID_DATA_FILE}"),
            MOCK_INPUT_BUCKET,
            f"{VALID_DATA_FILE}",
        )

        yield


@pytest.fixture
def create_buckets():
    with mock_s3():
        client = boto3.client("s3", region_name=REGION_NAME)
        client.create_bucket(
            Bucket=MOCK_INPUT_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
        )
        client.create_bucket(
            Bucket=MOCK_OUTPUT_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
        )

        yield


@pytest.fixture
@freeze_time("2021-06-29 10:00")
def upload_existing_gp_data(create_buckets):
    client = boto3.client("s3", region_name=REGION_NAME)
    client.upload_file(
        os.path.join(DATA, f"{EXISTING_GP_FILE}"),
        MOCK_OUTPUT_BUCKET,
        f"{EXISTING_GP_FILE}",
    )


@pytest.fixture
def upload_valid_dps_data_with_existing_gp_data(create_buckets):
    client = boto3.client("s3", region_name=REGION_NAME)
    client.upload_file(
        os.path.join(DATA, f"{VALID_DATA_FILE}"),
        MOCK_INPUT_BUCKET,
        f"{VALID_DATA_FILE}",
    )


@pytest.fixture
def upload_invalid_dps_data_to_s3():
    with mock_s3():
        client = boto3.client("s3", region_name=REGION_NAME)
        client.create_bucket(
            Bucket=MOCK_INPUT_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
        )
        client.create_bucket(
            Bucket=MOCK_OUTPUT_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
        )
        client.upload_file(
            os.path.join(DATA, f"{INVALID_DATA_FILE}"),
            MOCK_INPUT_BUCKET,
            f"{INVALID_DATA_FILE}",
        )

        yield


@pytest.fixture
def create_dynamodb_tables():
    with mock_dynamodb2():
        Errors.create_table()
        yield
