import time

import json
import os

import boto3
import pytest
from moto import mock_s3, mock_ssm

from lr_25_mesh_post_office.lr_25_lambda_handler import MeshPostOffice

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "..", "_data", "unit")

AWS_LAMBDA_FUNCTION_NAME = "LR_25_mesh_post_office"
DATA_FILE = "C86543.csv"
MOCK_INBOUND_BUCKET = "mesh-bucket"
MOCK_INBOUND_KEY = "inbound_X00000"
MOCK_OUTPUT_BUCKET = "lr-01-input"
MOCK_OUTPUT_KEY = "inbound"
REGION_NAME = os.environ.get("AWS_REGION")


@pytest.fixture(autouse=True)
def mesh_post_office_env_setup():
    """
    In every test, set the environ to minimally mimic what Lambda runtime sets,
    which LambdaApplication uses to find SSM Params
    """
    os.environ["AWS_LAMBDA_FUNCTION_NAME"] = AWS_LAMBDA_FUNCTION_NAME


@pytest.fixture
def mesh_post_office_open(
    create_mock_ssm_param_mesh_post_office_open,
    create_mock_ssm_param_mappings_single,
    upload_mesh_message_to_s3,
):
    return MeshPostOffice()


@pytest.fixture
def mesh_post_office_closed(
    create_mock_ssm_param_mesh_post_office_closed, create_mock_ssm_param_mappings_single
):
    return MeshPostOffice()


@pytest.fixture
def mesh_post_office_open_multiple_mappings(
    create_mock_ssm_param_mesh_post_office_open,
    create_mock_ssm_param_mappings_multiple,
    upload_mesh_messages_to_s3,
):
    return MeshPostOffice()


@pytest.fixture
def create_mock_ssm_param_mesh_post_office_open(ssm):
    ssm.put_parameter(
        Name=f"/{AWS_LAMBDA_FUNCTION_NAME}/mesh_post_office_open",
        Value="True",
        Type="String",
        Overwrite=True,
    )
    yield


@pytest.fixture
def create_mock_ssm_param_mesh_post_office_closed(ssm):
    ssm.put_parameter(
        Name=f"/{AWS_LAMBDA_FUNCTION_NAME}/mesh_post_office_open",
        Value="False",
        Type="String",
        Overwrite=True,
    )
    yield


@pytest.fixture
def create_mock_ssm_param_mappings_single(ssm):
    mappings = json.dumps(
        [
            {
                "inbound": {"bucket": MOCK_INBOUND_BUCKET, "key": MOCK_INBOUND_KEY},
                "outbound": {"bucket": MOCK_OUTPUT_BUCKET, "key": MOCK_OUTPUT_KEY},
            }
        ]
    )
    ssm.put_parameter(
        Name=f"/{AWS_LAMBDA_FUNCTION_NAME}/mappings",
        Value=str(mappings),
        Type="String",
        Overwrite=True,
    )
    yield


@pytest.fixture
def create_mock_ssm_param_mappings_multiple(ssm):
    mappings = json.dumps(
        [
            {
                "inbound": {"bucket": MOCK_INBOUND_BUCKET, "key": MOCK_INBOUND_KEY},
                "outbound": {"bucket": MOCK_OUTPUT_BUCKET, "key": MOCK_OUTPUT_KEY},
            },
            {
                "inbound": {"bucket": f"{MOCK_INBOUND_BUCKET}2", "key": f"{MOCK_INBOUND_KEY}2"},
                "outbound": {"bucket": f"{MOCK_OUTPUT_BUCKET}2", "key": f"{MOCK_OUTPUT_KEY}2"},
            },
        ]
    )
    ssm.put_parameter(
        Name=f"/{AWS_LAMBDA_FUNCTION_NAME}/mappings",
        Value=str(mappings),
        Type="String",
        Overwrite=True,
    )
    yield


@pytest.fixture
def upload_mesh_message_to_s3(s3):
    s3.create_bucket(
        Bucket=MOCK_INBOUND_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
    )
    s3.create_bucket(
        Bucket=MOCK_OUTPUT_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
    )
    s3.put_object(Bucket=MOCK_INBOUND_BUCKET, Key=f"{MOCK_INBOUND_KEY}/")
    s3.upload_file(
        os.path.join(DATA, DATA_FILE),
        MOCK_INBOUND_BUCKET,
        os.path.join(MOCK_INBOUND_KEY, DATA_FILE),
    )


@pytest.fixture
def upload_mesh_messages_to_s3(s3):
    s3.create_bucket(
        Bucket=MOCK_INBOUND_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
    )
    s3.create_bucket(
        Bucket=f"{MOCK_INBOUND_BUCKET}2",
        CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
    )
    s3.create_bucket(
        Bucket=MOCK_OUTPUT_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
    )
    s3.create_bucket(
        Bucket=f"{MOCK_OUTPUT_BUCKET}2",
        CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
    )
    s3.put_object(Bucket=MOCK_INBOUND_BUCKET, Key=f"{MOCK_INBOUND_KEY}/")
    s3.put_object(Bucket=f"{MOCK_INBOUND_BUCKET}2", Key=f"{MOCK_INBOUND_KEY}/")
    s3.upload_file(
        os.path.join(DATA, DATA_FILE),
        MOCK_INBOUND_BUCKET,
        os.path.join(MOCK_INBOUND_KEY, DATA_FILE),
    )
    s3.upload_file(
        os.path.join(DATA, DATA_FILE),
        f"{MOCK_INBOUND_BUCKET}2",
        os.path.join(f"{MOCK_INBOUND_KEY}2", DATA_FILE),
    )


@pytest.fixture(scope="function")
def s3():
    with mock_s3():
        yield boto3.client("s3", region_name=REGION_NAME)


@pytest.fixture(scope="function")
def ssm():
    with mock_ssm():
        yield boto3.client("ssm", region_name=REGION_NAME)
