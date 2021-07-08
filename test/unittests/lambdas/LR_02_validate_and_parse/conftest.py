import os
import boto3
import pytest

from moto import mock_dynamodb2, mock_s3, mock_sqs

from lambda_code.LR_02_validate_and_parse.lr_02_lambda_handler import LR02LambdaHandler
from utils.database.models import Demographics, Errors, Jobs, InFlight

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

MOCK_BUCKET = os.environ.get("AWS_S3_REGISTRATION_EXTRACT_BUCKET")
MOCK_QUEUE = os.environ.get("AWS_PATIENT_RECORD_SQS")
REGION_NAME = os.environ.get("AWS_REGION")

JOB_ID = "50e1b957-2fc4-44b0-8e60-d8f9ca162099"

VALID_FILE = "A82023_GPR4LNA1.CSA"
INVALID_FILE = "A82023_GPR4LNA1.CSB"


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
def upload_valid_mock_data_to_s3(create_bucket):
    client = boto3.client("s3")
    client.upload_file(
        os.path.join(DATA, f"{VALID_FILE}"),
        MOCK_BUCKET,
        f"inbound/{VALID_FILE}"
    )


@pytest.fixture
def upload_invalid_mock_data_to_s3(create_bucket):
    client = boto3.client("s3")
    client.upload_file(
        os.path.join(DATA, f"{INVALID_FILE}"),
        MOCK_BUCKET,
        f"inbound/{INVALID_FILE}",
    )


@pytest.fixture
def create_dynamodb_tables():
    with mock_dynamodb2():
        Errors.create_table()
        Demographics.create_table()
        Jobs.create_table()
        InFlight.create_table()
        yield


@pytest.fixture
def create_sqs():
    with mock_sqs():
        sqs_client = boto3.client("sqs", region_name=REGION_NAME)

        attributes = {
            "DelaySeconds": "900",
            "MaximumMessageSize": "256000",
            "MessageRetentionPeriod": "345600",
            "ReceiveMessageWaitTimeSeconds": "20",
            "VisibilityTimeout": "30",
        }

        sqs_client.create_queue(QueueName=MOCK_QUEUE, Attributes=attributes)
        yield


@pytest.fixture(scope="module")
def lr_02_valid_file_event():
    return {"Records": [{"s3": {"object": {"key": f"inbound/{VALID_FILE}"}}}]}


@pytest.fixture(scope="module")
def lr_02_invalid_file_event():
    return {"Records": [{"s3": {"object": {"key": f"inbound/{INVALID_FILE}"}}}]}


@pytest.fixture(scope="module")
def lambda_handler():
    app = LR02LambdaHandler()
    return app
