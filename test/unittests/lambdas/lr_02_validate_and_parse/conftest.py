import io
import os
import textwrap
import zipfile

import boto3
import pytest
from moto import mock_dynamodb2, mock_s3, mock_iam, mock_lambda

from lambda_code.lr_02_validate_and_parse.lr_02_lambda_handler import ValidateAndParse
from utils.database.models import Jobs, InFlight

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

MOCK_BUCKET = os.environ.get("AWS_S3_REGISTRATION_EXTRACT_BUCKET")
REGION_NAME = os.environ.get("AWS_REGION")

JOB_ID = "50e1b957-2fc4-44b0-8e60-d8f9ca162099"

VALID_FILE = "A82023_GPR4LNA1.CSA"
INVALID_FILE = "A12023_GPR4LNA1.CSB"


@pytest.fixture
def create_bucket(s3):
    s3.create_bucket(
        Bucket=MOCK_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
    )


@pytest.fixture
def upload_valid_mock_data_to_s3(s3, create_bucket):
    s3.upload_file(os.path.join(DATA, f"{VALID_FILE}"), MOCK_BUCKET, f"inbound/{VALID_FILE}")


@pytest.fixture
def upload_invalid_mock_data_to_s3(s3, create_bucket):
    s3.upload_file(
        os.path.join(DATA, f"{INVALID_FILE}"),
        MOCK_BUCKET,
        f"inbound/{INVALID_FILE}",
    )


@pytest.fixture
def create_dynamodb_tables(dynamodb):
    Jobs.create_table()
    InFlight.create_table()


def get_role_name(iam):
    return iam.create_role(
        RoleName="my-role",
        AssumeRolePolicyDocument="some policy",
        Path="/my-path/",
    )["Role"]["Arn"]


def _process_lambda(func_str):
    zip_output = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_output, "w", zipfile.ZIP_DEFLATED)
    zip_file.writestr("main.py", func_str)
    zip_file.close()
    zip_output.seek(0)
    return zip_output.read()


@pytest.fixture
def create_lr_24_lambda(lambda_, iam):
    func_str = textwrap.dedent(
        """
        def lambda_handler(event, context):
            pass
        """
    )

    lambda_.create_function(
        FunctionName=os.getenv("LR_24_SAVE_RECORDS_TO_S3"),
        Runtime="python3.8",
        Role=get_role_name(iam),
        Handler="main.lambda_handler",
        Code={
            "ZipFile": _process_lambda(func_str),
        },
        Publish=True,
        Timeout=10,
        MemorySize=128,
    )


@pytest.fixture(scope="module")
def lr_02_valid_file_event():
    return {"Records": [{"s3": {"object": {"key": f"inbound/{VALID_FILE}"}}}]}


@pytest.fixture(scope="module")
def lr_02_invalid_file_event():
    return {"Records": [{"s3": {"object": {"key": f"inbound/{INVALID_FILE}"}}}]}


@pytest.fixture
def lambda_handler(s3, lambda_, iam, dynamodb):
    return ValidateAndParse()


@pytest.fixture(scope="function")
def s3():
    with mock_s3():
        yield boto3.client("s3")


@pytest.fixture(scope="function")
def lambda_():
    with mock_lambda():
        yield boto3.client("lambda")


@pytest.fixture(scope="function")
def iam():
    with mock_iam():
        yield boto3.client("iam")


@pytest.fixture(scope="function")
def dynamodb():
    with mock_dynamodb2():
        yield boto3.client("dynamodb")
