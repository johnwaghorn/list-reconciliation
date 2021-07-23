import os
import boto3
import pytest

from freezegun import freeze_time
from moto import mock_dynamodb2, mock_s3

from lambda_code.LR_04_feedback_failure.lr_04_lambda_handler import FeedbackFailure
from utils import get_datetime_now
from utils.database.models import Errors

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

MOCK_BUCKET = os.environ.get("AWS_S3_REGISTRATION_EXTRACT_BUCKET")
REGION_NAME = os.environ.get("AWS_REGION")

JOB_ID = "50e1b957-2fc4-44b0-8e60-d8f9ca162099"
PRACTICE_CODE = "A82023"

FAILED_FILE = "A12023_GPR4LNA1.CSB"
LOG_FILE = "A12023_GPR4LNA1.CSB_LOG_06042020T1440.00.000000.json"


@pytest.fixture
def create_bucket():
    with mock_s3():
        client = boto3.client("s3")
        client.create_bucket(
            Bucket=MOCK_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
        )
        yield


@pytest.fixture
def upload_mock_data_to_s3(create_bucket):
    client = boto3.client("s3")
    client.upload_file(os.path.join(DATA, f"{FAILED_FILE}"), MOCK_BUCKET, f"fail/{FAILED_FILE}")
    client.upload_file(os.path.join(DATA, f"{LOG_FILE}"), MOCK_BUCKET, f"fail/logs/{LOG_FILE}")


@pytest.fixture
def create_dynamodb_tables():
    with mock_dynamodb2():
        Errors.create_table()
        yield


@pytest.fixture(scope="module")
def lr_04_event():
    return {"Records": [{"s3": {"object": {"key": f"fail/logs/{LOG_FILE}"}}}]}


@pytest.fixture(scope="module")
def lambda_handler():
    app = FeedbackFailure()
    return app
