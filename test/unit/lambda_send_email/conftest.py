import os

import boto3
import pytest
from lambda_send_email.lambda_handler import SendEmail
from moto import mock_s3, mock_ssm

REGION_NAME = os.environ.get("AWS_REGION")
EMAIL_SSM_PREFIX = os.getenv("EMAIL_SSM_PREFIX")
LISTREC_EMAIL_PASSWORD = os.getenv("LISTREC_EMAIL_PASSWORD")
EMAIL_BUCKET = os.environ.get("AWS_S3_SEND_EMAIL_BUCKET")
EMAIL_FILE = "email.json"

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "..", "_data", "unit")


@pytest.fixture
def s3():
    with mock_s3():
        yield boto3.client("s3", region_name=REGION_NAME)


@pytest.fixture
def create_bucket(s3):
    s3.create_bucket(
        Bucket=EMAIL_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
    )

    yield


@pytest.fixture
def upload_email_file(create_bucket, s3):
    s3.upload_file(
        os.path.join(DATA, "email.json"),
        EMAIL_BUCKET,
        "email.json",
    )


@pytest.fixture
def lambda_handler(ssm, email_ssm, mock_send_email):
    app = SendEmail()
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


@pytest.fixture
def mock_send_email(monkeypatch):
    monkeypatch.setattr("send_email.send", lambda w, x, y: None)
