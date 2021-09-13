import os
from datetime import datetime

import boto3
import pytest
from moto import mock_dynamodb2, mock_s3

from lr_12_pds_registration_status.lr_12_lambda_handler import (
    PDSRegistrationStatus,
)
from database.models import Demographics, Jobs, JobStats


ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "..", "_data", "unit")

AWS_REGION = os.getenv("AWS_REGION")
LR_13_REGISTRATIONS_OUTPUT_BUCKET = os.getenv("LR_13_REGISTRATIONS_OUTPUT_BUCKET")
LR_22_PDS_PRACTICE_REGISTRATIONS_BUCKET = os.getenv("LR_22_PDS_PRACTICE_REGISTRATIONS_BUCKET")


@pytest.fixture(scope="module")
def lr_12_event():
    return {"job_id": "blah"}


@pytest.fixture(scope="function")
def lambda_handler(mock_pds_app_key, mock_pds_access_token, mock_pds_private_key):
    app = PDSRegistrationStatus()
    return app


PATIENTS = [
    Demographics(
        "29263475-1c38-4d2e-a477-0004ba9f04b2",
        "ABC123",
        GP_GpPracticeCode="Y123452",
        GP_HaCipher="123",
        GP_TransactionDate="123",
        GP_TransactionId="123",
        GP_TransactionTime="123",
        NhsNumber="1000000010",
    ),
    Demographics(
        "31c8aa5e-c545-11eb-ae00-5b6c199ee918",
        "ABC123",
        GP_GpPracticeCode="Y123452",
        GP_HaCipher="456",
        GP_TransactionDate="123",
        GP_TransactionId="123",
        GP_TransactionTime="123",
        NhsNumber="1100000011",
    ),
    Demographics(
        "3b4233a6-cdbb-11eb-ac06-7bab1fa0ee1f",
        "XYZ567",
        GP_GpPracticeCode="Y123451",
        GP_HaCipher="456",
        GP_TransactionDate="123",
        GP_TransactionId="123",
        GP_TransactionTime="123",
        NhsNumber="8000000008",
    ),
]


@pytest.fixture
def dynamodb():
    with mock_dynamodb2():
        Demographics.create_table()
        Jobs.create_table()
        JobStats.create_table()
        yield


@pytest.fixture
def demographics(dynamodb):
    with Demographics.batch_write() as batch:
        for data in PATIENTS:
            batch.save(data)

    yield


@pytest.fixture
def jobstats(dynamodb):
    JobStats("ABC123").save()
    JobStats("XYZ567").save()
    yield


@pytest.fixture
def jobs(dynamodb):
    job = Jobs(
        "XYZ567",
        PracticeCode="Y123451",
        FileName="Y123451.E1A",
        StatusId="1",
        Timestamp=datetime(2021, 5, 27, 14, 48, 37),
    )

    job.save()

    job = Jobs(
        "ABC123",
        PracticeCode="Y123452",
        FileName="Y123452.E1A",
        StatusId="1",
        Timestamp=datetime(2021, 5, 27, 14, 48, 37),
    )

    job.save()
    yield


@pytest.fixture
def s3():
    with mock_s3():
        s3 = boto3.client("s3", region_name=AWS_REGION)
        s3.create_bucket(
            Bucket=LR_13_REGISTRATIONS_OUTPUT_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )

        s3.create_bucket(
            Bucket=LR_22_PDS_PRACTICE_REGISTRATIONS_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )
        for file in ("Y123451.csv", "Y123452.csv"):
            s3.upload_file(os.path.join(DATA, file), LR_22_PDS_PRACTICE_REGISTRATIONS_BUCKET, file)

        s3.create_bucket(
            Bucket="mock-pds-data",
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )
        s3.upload_file(os.path.join(DATA, "pds_api_data.csv"), "mock-pds-data", "pds_api_data.csv")
        yield
