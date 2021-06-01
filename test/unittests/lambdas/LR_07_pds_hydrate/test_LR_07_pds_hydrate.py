import io
import os
import textwrap
import zipfile

from botocore.exceptions import ClientError
from moto import mock_dynamodb2, mock_s3, mock_lambda, mock_iam

import boto3
import pytest

from lambdas.LR_07_pds_hydrate.pds_hydrate import pds_hydrate
from utils.models import Demographics, Errors
from utils.pds_api_service import PDSAPIError

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
        try:
            return iam.get_role(RoleName="my-role")["Role"]["Arn"]
        except ClientError:
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
def demographics_record(create_dynamodb_tables):
    item = {
        "Id": "50",
        "JobId": "50",
        "NhsNumber": "9000000009",
        "GP_DateOfBirth": "20101025",
        "GP_Gender": "female",
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
    }

    obj = Demographics(item["Id"], item["JobId"], **item)
    obj.save()
    yield item


def test_write_into_table(
    upload_pds_mock_data_to_s3, demographics_record, create_LR08_demographic_comparison_lambda
):

    response = pds_hydrate("9000000009", "50", "50")

    assert response == {
        "status": "success",
        "message": "Retrieved PDS data for NhsNumber: 9000000009, JobId: 50, PatientId: 50",
    }

    actual = Demographics.get("50", "50").attribute_values

    demographics_record.update(
        {
            "PDS_GpCode": "Y123452",
            "PDS_GpRegisteredDate": "2012-05-22",
            "PDS_Surname": "Smith",
            "PDS_Forenames": ["Jane"],
            "PDS_Titles": ["Mrs"],
            "PDS_Gender": "female",
            "PDS_DateOfBirth": "2010-10-22",
            "PDS_IsSensitive": False,
            "PDS_Address": [
                "1 Trevelyan Square",
                "Boar Lane",
                "City Centre",
                "Leeds",
                "West Yorkshire",
            ],
            "PDS_PostCode": "LS1 6AE",
        }
    )

    assert actual == demographics_record


def test_bad_nhs_number_raises_PDSAPIError(
    upload_pds_mock_data_to_s3, demographics_record, create_LR08_demographic_comparison_lambda
):
    with pytest.raises(PDSAPIError):
        pds_hydrate("1", "50", "50")


def test_record_doesnt_exist_raises_DemographicsDoesNotExist(
    upload_pds_mock_data_to_s3, demographics_record, create_LR08_demographic_comparison_lambda
):
    with pytest.raises(Demographics.DoesNotExist):
        pds_hydrate("9000000009", "500", "500")
