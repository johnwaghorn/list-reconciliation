import os

import boto3
import pytest
from lr_04_feedback_failure.lr_04_lambda_handler import FeedbackFailure
from moto import mock_s3, mock_ssm

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "..", "_data", "unit")

REGION_NAME = os.environ.get("AWS_REGION")
MOCK_BUCKET = os.environ.get("AWS_S3_REGISTRATION_EXTRACT_BUCKET")
EMAIL_SSM_PREFIX = os.getenv("EMAIL_SSM_PREFIX")
LISTREC_EMAIL_PASSWORD = os.getenv("LISTREC_EMAIL_PASSWORD")

FAILED_FILE = "A12023_GPR4LNA1.CSB"
LOG_FILE = "A12023_GPR4LNA1.CSB-FailedFile-50e1b957-2fc4-44b0-8e60-d8f9ca162099.json"
INVALID_LOG_FILE = "A12023_GPR4LNA1.CSB-FailedFile-00000000-0000-0000-0000-0000000000000.json"


@pytest.fixture
def create_bucket():
    with mock_s3():
        client = boto3.client("s3")
        client.create_bucket(
            Bucket=MOCK_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
        )
        client.upload_file(os.path.join(DATA, f"{FAILED_FILE}"), MOCK_BUCKET, f"fail/{FAILED_FILE}")
        yield


@pytest.fixture
def upload_invalid_log_to_s3(create_bucket):
    client = boto3.client("s3")
    client.upload_file(
        os.path.join(DATA, f"{INVALID_LOG_FILE}"), MOCK_BUCKET, f"fail/logs/{INVALID_LOG_FILE}"
    )


@pytest.fixture
def upload_valid_log_to_s3(create_bucket):
    client = boto3.client("s3")
    client.upload_file(os.path.join(DATA, f"{LOG_FILE}"), MOCK_BUCKET, f"fail/logs/{LOG_FILE}")


@pytest.fixture(scope="module")
def lr_04_event_valid_file():
    return {"Records": [{"s3": {"object": {"key": f"fail/logs/{LOG_FILE}"}}}]}


@pytest.fixture(scope="module")
def lr_04_event_invalid_file():
    return {"Records": [{"s3": {"object": {"key": f"fail/logs/{INVALID_LOG_FILE}"}}}]}


@pytest.fixture
def lambda_handler(ssm, email_ssm, mock_email):
    app = FeedbackFailure()
    return app


@pytest.fixture
def ssm():
    with mock_ssm():
        yield boto3.client("ssm", region_name=REGION_NAME)


@pytest.fixture
def email_ssm(ssm):
    ssm.put_parameter(
        Name=f"{EMAIL_SSM_PREFIX}/list_rec_email_password",
        Value=LISTREC_EMAIL_PASSWORD,
        Type="SecureString",
        Overwrite=True,
    )
    yield
