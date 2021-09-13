import os
from datetime import datetime

import boto3
import pytest
from moto import mock_dynamodb2, mock_s3

from lr_11_gp_registration_status.lr_11_lambda_handler import (
    GPRegistrations,
)
from database.models import Demographics, Jobs, JobStats


AWS_REGION = os.getenv("AWS_REGION")
LR_13_REGISTRATIONS_OUTPUT_BUCKET = os.getenv("LR_13_REGISTRATIONS_OUTPUT_BUCKET")


@pytest.fixture(scope="module")
def lr_12_event():
    return {"job_id": "blah"}


@mock_s3
@pytest.fixture(scope="module")
def lambda_handler():
    app = GPRegistrations()
    return app


PATIENTS = [
    Demographics(
        "d2305c19-96b3-4e81-91af-d26f2281b67f",
        "1",
        GP_GpPracticeCode="Y12345",
        GP_HaCipher="123",
        GP_TransactionDate="123",
        GP_TransactionId="123",
        GP_TransactionTime="123",
        NhsNumber="1231",
        GP_RegistrationStatus="Matched",
        GP_Surname="Smith",
        GP_Forenames="John Paul",
        GP_DateOfBirth="2004-05-01",
        GP_AddressLine1="1 Park Street",
        GP_AddressLine2="",
        GP_AddressLine3="",
        GP_AddressLine4="",
        GP_AddressLine5="Manchester",
        GP_PostCode="LA1 234",
        GP_Title="Mr",
        GP_Gender="1",
        PDS_GpRegisteredDate=None,
        PDS_Sensitive="U",
    ),
    Demographics(
        "29263475-1c38-4d2e-a477-0004ba9f04b2",
        "1",
        GP_GpPracticeCode="Y12345",
        GP_HaCipher="123",
        GP_TransactionDate="123",
        GP_TransactionId="123",
        GP_TransactionTime="123",
        NhsNumber="1232",
        GP_RegistrationStatus="Unmatched",
        GP_Surname="Corden",
        GP_Forenames="Steve",
        GP_DateOfBirth="2004-05-01",
        GP_AddressLine1="1 Park Street",
        GP_AddressLine2="",
        GP_AddressLine3="",
        GP_AddressLine4="",
        GP_AddressLine5="Manchester",
        GP_PostCode="LA1 234",
        GP_Title="Dr",
        GP_Gender="0",
        PDS_GpRegisteredDate="2019-04-01",
        PDS_Sensitive="U",
    ),
    Demographics(
        "31c8aa5e-c545-11eb-ae00-5b6c199ee918",
        "1",
        GP_GpPracticeCode="Y12345",
        GP_HaCipher="123",
        GP_TransactionDate="123",
        GP_TransactionId="123",
        GP_TransactionTime="123",
        NhsNumber="1233",
        GP_RegistrationStatus="Deducted Patient Match",
        GP_Surname="Davis",
        GP_Forenames="Jane",
        GP_DateOfBirth="2004-05-01",
        GP_AddressLine1="1 Park Street",
        GP_AddressLine2="",
        GP_AddressLine3="",
        GP_AddressLine4="",
        GP_AddressLine5="Manchester",
        GP_PostCode="LA1 234",
        GP_Title="Maj",
        GP_Gender="1",
        PDS_GpRegisteredDate="2019-04-02",
        PDS_Sensitive="U",
    ),
    Demographics(
        "37c100aa-c545-11eb-a75b-1315385e9b21",
        "1",
        GP_GpPracticeCode="Y12345",
        GP_HaCipher="123",
        GP_TransactionDate="123",
        GP_TransactionId="123",
        GP_TransactionTime="123",
        NhsNumber="1234",
        GP_RegistrationStatus="Partnership Mismatch",
        GP_Surname="Frost",
        GP_Forenames="Chris",
        GP_DateOfBirth="2004-05-01",
        GP_AddressLine1="1 Park Street",
        GP_AddressLine2="",
        GP_AddressLine3="",
        GP_AddressLine4="",
        GP_AddressLine5="Manchester",
        GP_PostCode="LA1 234",
        GP_Title="Miss",
        GP_Gender="2",
        PDS_GpRegisteredDate="2019-04-03",
        PDS_Sensitive="U",
    ),
    Demographics(
        "6cea6924-1ed9-423e-a69f-6d868f58b278",
        "2",
        GP_GpPracticeCode="ABC",
        GP_HaCipher="123",
        GP_TransactionDate="123",
        GP_TransactionId="123",
        GP_TransactionTime="123",
        NhsNumber="1235",
        GP_RegistrationStatus="Matched",
        PDS_Sensitive="U",
    ),
    Demographics(
        "50e1b957-2fc4-44b0-8e60-d8f9ca162022",
        "2",
        GP_GpPracticeCode="ABC",
        GP_HaCipher="123",
        GP_TransactionDate="123",
        GP_TransactionId="123",
        GP_TransactionTime="123",
        NhsNumber="1236",
        GP_RegistrationStatus="Matched",
        PDS_Sensitive="U",
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
    JobStats("1").save()
    JobStats("2").save()
    yield


@pytest.fixture
def jobs(dynamodb):
    job = Jobs(
        "1",
        PracticeCode="Y12345",
        FileName="Y12345.E1A",
        StatusId="1",
        Timestamp=datetime(2021, 5, 27, 14, 48, 37),
    )

    job.save()

    job = Jobs(
        "2",
        PracticeCode="Y23456",
        FileName="Y23456.E1A",
        StatusId="1",
        Timestamp=datetime(2021, 5, 27, 14, 48, 37),
    )

    job.save()
    yield


@pytest.fixture
def s3_bucket():
    with mock_s3():
        client = boto3.client("s3", region_name=AWS_REGION)
        client.create_bucket(
            Bucket=LR_13_REGISTRATIONS_OUTPUT_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )
        return client
