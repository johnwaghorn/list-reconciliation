import io
import os
import textwrap
import zipfile

import boto3
import pytest
from database.models import Demographics
from lr_07_pds_hydrate.lr_07_lambda_handler import PdsHydrate
from moto import mock_dynamodb2, mock_iam, mock_lambda, mock_s3

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "..", "_data", "unit")

REGION_NAME = "eu-west-2"


@pytest.fixture(scope="function")
def lambda_handler(mock_pds_app_key, mock_pds_access_token, mock_pds_private_key):
    app = PdsHydrate()
    return app


@pytest.fixture
def upload_pds_mock_data_to_s3():
    with mock_s3():
        client = boto3.client("s3", region_name=REGION_NAME)
        client.create_bucket(
            Bucket="mock-pds-data",
            CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
        )
        client.upload_file(
            os.path.join(DATA, "pds_api_data.csv"), "mock-pds-data", "pds_api_data.csv"
        )
        yield


@pytest.fixture
def create_dynamodb_tables():
    with mock_dynamodb2():
        Demographics.create_table()
        yield


def get_role_name():
    with mock_iam():
        iam = boto3.client("iam", region_name=REGION_NAME)
        return iam.create_role(
            RoleName="my-role",
            AssumeRolePolicyDocument="some policy",
            Path="/my-path/",
        )["Role"]["Arn"]


def _process_lambda(func_str):
    zip_output = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_output, "w", zipfile.ZIP_DEFLATED)
    zip_file.writestr("lambda_function.py", func_str)
    zip_file.close()
    zip_output.seek(0)
    return zip_output.read()


@pytest.fixture
def create_LR08_demographic_comparison_lambda():
    func_str = textwrap.dedent(
        """
        def pds_hydrate(event, context):
            pass
        """
    )

    with mock_lambda():
        client = boto3.client("lambda", region_name=REGION_NAME)
        client.create_function(
            FunctionName=os.getenv("DEMOGRAPHIC_COMPARISON_LAMBDA"),
            Runtime="python3.8",
            Role=get_role_name(),
            Handler="lambda_function.pds_hydrate",
            Code={
                "ZipFile": _process_lambda(func_str),
            },
            Publish=True,
            Timeout=10,
            MemorySize=128,
        )
        yield
