import os

import boto3
import pytest

from moto import mock_s3, mock_dynamodb2

from lambda_code.LR_24_save_records_to_s3.lr24_lambda_handler import SaveRecordsToS3
from utils.database.models import Errors

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

LR_06_BUCKET = os.environ.get("LR_06_BUCKET")
REGION_NAME = os.environ.get("AWS_REGION")


@pytest.fixture
def s3():
    with mock_s3():
        client = boto3.client("s3")
        client.create_bucket(
            Bucket=LR_06_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
        )
        yield


@pytest.fixture
def create_dynamodb_tables():
    with mock_dynamodb2():
        Errors.create_table()
        yield


@pytest.fixture
def lambda_handler():
    app = SaveRecordsToS3()
    return app


@pytest.fixture
def records():
    return [
        {
            "job_id": "789",
            "practice_code": "Y12345",
            "id": "1234566",
            "NHS_NUMBER": "12345",
            "TRADING_PARTNER_NHAIS_CIPHER": "LA1",
            "DATE_OF_DOWNLOAD": "2012-01-04 15:00:00",
            "TRANS_ID": "15345",
            "SURNAME": "SMITH",
            "FORENAMES": "JOHN",
            "PREV_SURNAME": "",
            "TITLE": "MR",
            "SEX": "MALE",
            "DOB": "1985-21-04",
            "ADDRESS_LINE1": "12 ORCHARD WAY",
            "ADDRESS_LINE2": "",
            "ADDRESS_LINE3": "MAIDENHEAD",
            "ADDRESS_LINE4": "",
            "ADDRESS_LINE5": "",
            "POSTCODE": "HP14 2YQ",
            "DRUGS_DISPENSED_MARKER": False,
        },
        {
            "job_id": "789",
            "practice_code": "Y12345",
            "id": "1234567",
            "NHS_NUMBER": "12346",
            "TRADING_PARTNER_NHAIS_CIPHER": "LA1",
            "DATE_OF_DOWNLOAD": "2012-01-04 15:00:00",
            "TRANS_ID": "12545",
            "SURNAME": "JONES",
            "FORENAMES": "MARK",
            "PREV_SURNAME": "",
            "TITLE": "MR",
            "SEX": "MALE",
            "DOB": "1985-21-04",
            "ADDRESS_LINE1": "THE COTTAGE",
            "ADDRESS_LINE2": "",
            "ADDRESS_LINE3": "",
            "ADDRESS_LINE4": "LEEDS",
            "ADDRESS_LINE5": "",
            "POSTCODE": "LE1 1JD",
            "DRUGS_DISPENSED_MARKER": False,
        },
    ]
