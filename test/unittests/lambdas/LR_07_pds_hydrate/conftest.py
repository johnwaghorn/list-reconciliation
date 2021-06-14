import io
import os
import textwrap
import zipfile

from moto import mock_dynamodb2, mock_s3, mock_lambda, mock_iam

import boto3
import pytest

from utils.models import Demographics, Errors

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

REGION_NAME = "eu-west-2"


@pytest.fixture
def upload_pds_mock_data_to_s3():
    with mock_s3():
        client = boto3.client("s3", region_name=REGION_NAME)
        client.create_bucket(
            Bucket="mock-pds-data", CreateBucketConfiguration={"LocationConstraint": REGION_NAME}
        )
        client.upload_file(
            os.path.join(DATA, "pds_api_data.csv"), "mock-pds-data", "pds_api_data.csv"
        )
        yield


@pytest.fixture
def create_dynamodb_tables():
    with mock_dynamodb2():
        Errors.create_table()
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


@pytest.fixture
def demographics_records(create_dynamodb_tables):
    items = [
        {
            "Id": "50",
            "JobId": "50",
            "NhsNumber": "9000000009",
            "GP_DateOfBirth": "20101025",
            "GP_Gender": "2",
            "GP_GpCode": "Y123452",
            "GP_Title": "Mrs",
            "GP_Forenames": "Jane",
            "GP_Surname": "Smith",
            "GP_AddressLine1": "1 Trevelyan Square",
            "GP_AddressLine2": "Boar's Head Lane",
            "GP_AddressLine3": "City Centre",
            "GP_AddressLine4": "Leeds",
            "GP_AddressLine5": "West Yorkshire",
            "GP_PostCode": "LS1 6AE",
            "IsComparisonCompleted": False,
            "GP_HaCipher": "TEST",
            "GP_TransactionDate": "2021-01-01",
            "GP_TransactionTime": "01:00:00",
            "GP_TransactionId": "1234",
            "GP_PreviousSurname": "TEST",
            "GP_DrugsDispensedMarker": "False",
        },
        {
            "Id": "51",
            "JobId": "50",
            "NhsNumber": "8000000008",
            "GP_DateOfBirth": "20091022",
            "GP_Gender": "1",
            "GP_GpCode": "Y123452",
            "GP_Title": "Mr",
            "GP_Forenames": "Paul Philip",
            "GP_Surname": "Davies",
            "GP_AddressLine1": "1 Trevelyan Square",
            "GP_AddressLine2": None,
            "GP_AddressLine3": None,
            "GP_AddressLine4": "Leeds",
            "GP_AddressLine5": "West Yorkshire",
            "GP_PostCode": "LS1 6UP",
            "IsComparisonCompleted": False,
            "GP_HaCipher": "TEST",
            "GP_TransactionDate": "2021-01-01",
            "GP_TransactionTime": "01:00:00",
            "GP_TransactionId": "1235",
            "GP_PreviousSurname": None,
            "GP_DrugsDispensedMarker": "False",
        },
        {
            "Id": "52",
            "JobId": "50",
            "NhsNumber": "7000000007",
            "GP_DateOfBirth": "19231121",
            "GP_Gender": "1",
            "GP_GpCode": "Y123452",
            "GP_Title": "Miss",
            "GP_Forenames": "Nikki-Stevens",
            "GP_Surname": "Pavey",
            "GP_AddressLine1": "19 Main Street",
            "GP_AddressLine2": None,
            "GP_AddressLine3": "Logan",
            "GP_AddressLine4": "Durham",
            "GP_AddressLine5": "London",
            "GP_PostCode": "ZE3 9JY",
            "IsComparisonCompleted": False,
            "GP_HaCipher": "TEST",
            "GP_TransactionDate": "2021-01-01",
            "GP_TransactionTime": "01:00:00",
            "GP_TransactionId": "1236",
            "GP_PreviousSurname": None,
            "GP_DrugsDispensedMarker": "False",
        },
        {
            "Id": "53",
            "JobId": "50",
            "NhsNumber": "6000000006",
            "GP_DateOfBirth": "19231121",
            "GP_Gender": "1",
            "GP_GpCode": "Y123452",
            "GP_Title": "Miss",
            "GP_Forenames": "Janet",
            "GP_Surname": "Wardle",
            "GP_AddressLine1": "18 Main Street",
            "GP_AddressLine2": None,
            "GP_AddressLine3": "Logan",
            "GP_AddressLine4": "Durham",
            "GP_AddressLine5": "London",
            "GP_PostCode": "ZE3 9JY",
            "IsComparisonCompleted": False,
            "GP_HaCipher": "TEST",
            "GP_TransactionDate": "2021-01-01",
            "GP_TransactionTime": "01:00:00",
            "GP_TransactionId": "1236",
            "GP_PreviousSurname": None,
            "GP_DrugsDispensedMarker": "False",
        },
    ]
    with Demographics.batch_write() as batch:
        records = [Demographics(item["Id"], item["JobId"], **item) for item in items]
        for record in records:
            batch.save(record)
    yield items
