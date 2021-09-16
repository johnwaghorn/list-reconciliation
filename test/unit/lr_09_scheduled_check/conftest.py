from datetime import datetime, timedelta

import boto3
import pytest
from database.models import Demographics, InFlight, Jobs, JobStats
from dateutil.parser import parse
from lr_09_scheduled_check.lr_09_lambda_handler import ScheduledCheck
from moto import mock_dynamodb2, mock_stepfunctions
from moto.core import ACCOUNT_ID

JOB_ID = {
    1: "b204b5f4-6762-414e-bb6b-a05c37f52956",
    2: "3af674be-1e7f-470c-b6d1-ca5ce6d9c600",
    3: "87e36ab6-4f25-4c47-9e13-d029f1e4c925",
    4: "87b687e3-6ad4-1337-0420-edcab6912499",
}
REGION_NAME = "eu-west-2"


@pytest.fixture(autouse=True)
def lambda_handler():
    app = ScheduledCheck()
    return app


FAKE_PATIENTS = [
    Demographics(
        Id="d2305c19-96b3-4e81-91af-d26f2281b67f",
        JobId=JOB_ID[1],
        NhsNumber="111",
        IsComparisonCompleted=True,
        GP_GpPracticeCode="JSABCDEF",
        PDS_GpPracticeCode="JSABCDEF",
        GP_HaCipher="123",
        GP_TransactionDate="1",
        GP_TransactionTime="1",
        GP_TransactionId="1",
    ),
    Demographics(
        Id="29263475-1c38-4d2e-a477-0004ba9f04b2",
        JobId=JOB_ID[1],
        NhsNumber="222",
        IsComparisonCompleted=True,
        GP_GpPracticeCode="JSABCDEF",
        PDS_GpPracticeCode="JSABCDEF",
        GP_HaCipher="123",
        GP_TransactionDate="1",
        GP_TransactionTime="1",
        GP_TransactionId="1",
    ),
    Demographics(
        Id="6cea6924-1ed9-423e-a69f-6d868f58b278",
        JobId=JOB_ID[1],
        NhsNumber="333",
        IsComparisonCompleted=True,
        GP_GpPracticeCode="JSABCDEF",
        PDS_GpPracticeCode="JSABCDEF",
        GP_HaCipher="123",
        GP_TransactionDate="1",
        GP_TransactionTime="1",
        GP_TransactionId="1",
    ),
    Demographics(
        Id="50e1b957-2fc4-44b0-8e60-d8f9ca162022",
        JobId=JOB_ID[1],
        NhsNumber="444",
        IsComparisonCompleted=True,
        GP_GpPracticeCode="JSABCDEF",
        PDS_GpPracticeCode="JSABCDEF",
        GP_HaCipher="123",
        GP_TransactionDate="1",
        GP_TransactionTime="1",
        GP_TransactionId="1",
    ),
    Demographics(
        Id="78490ae9-4908-4414-bf83-6b5452f18644",
        JobId=JOB_ID[1],
        NhsNumber="555",
        IsComparisonCompleted=True,
        GP_GpPracticeCode="JSABCDEF",
        PDS_GpPracticeCode="JSGHIJKLM",
        GP_HaCipher="123",
        GP_TransactionDate="1",
        GP_TransactionTime="1",
        GP_TransactionId="1",
    ),
    Demographics(
        Id="3af674be-1e7f-470c-b6d1-ca5ce6d9c600",
        JobId=JOB_ID[1],
        NhsNumber="666",
        IsComparisonCompleted=True,
        GP_GpPracticeCode="JSABCDEF",
        PDS_GpPracticeCode="JSGHIJKLM",
        GP_HaCipher="123",
        GP_TransactionDate="1",
        GP_TransactionTime="1",
        GP_TransactionId="1",
    ),
    Demographics(
        Id="3af674be-1e7f-470c-b6d1-ca5ce6d9c601",
        JobId=JOB_ID[3],
        NhsNumber="777",
        IsComparisonCompleted=False,
        GP_GpPracticeCode="JSABCDEG",
        PDS_GpPracticeCode="JSGHIJKLN",
        GP_HaCipher="123",
        GP_TransactionDate="1",
        GP_TransactionTime="1",
        GP_TransactionId="1",
    ),
]


@pytest.fixture
def create_dynamo_tables():
    with mock_dynamodb2():
        Demographics.create_table()
        InFlight.create_table()
        Jobs.create_table()
        JobStats.create_table()
        yield


@pytest.fixture
def populate_demographics_table(create_dynamo_tables):
    patients = FAKE_PATIENTS

    with Demographics.batch_write() as batch:
        for patient in patients:
            batch.save(patient)

    yield


@pytest.fixture
def populate_inflight_table(create_dynamo_tables):
    items = [
        InFlight(
            JOB_ID[1], TotalRecords=6, Timestamp=datetime.now() - timedelta(hours=1)
        ),
        InFlight(
            JOB_ID[2], TotalRecords=1, Timestamp=datetime.now() - timedelta(hours=1)
        ),
        InFlight(
            JOB_ID[3], TotalRecords=1, Timestamp=datetime.now() - timedelta(hours=1)
        ),
        InFlight(
            JOB_ID[4], TotalRecords=7, Timestamp=datetime.now() - timedelta(hours=9)
        ),
    ]

    with InFlight.batch_write() as batch:
        for item in items:
            batch.save(item)

    yield


@pytest.fixture
def populate_jobs_table(create_dynamo_tables):
    items = [
        Jobs(
            JOB_ID[1],
            PracticeCode="JSABCDEF",
            FileName="JSHTST.EAA",
            StatusId="1",
            Timestamp=parse("2021-05-27 14:48:37.274977"),
        ),
        Jobs(
            JOB_ID[4],
            PracticeCode="UINKJNKM",
            FileName="UINKJN.EAA",
            StatusId="1",
            Timestamp=parse("2021-05-27 14:48:37.274977"),
        ),
    ]

    with Jobs.batch_write() as batch:
        for item in items:
            batch.save(item)

    yield


@pytest.fixture
def mock_step_function():
    with mock_stepfunctions():
        client = boto3.client("stepfunctions", region_name=REGION_NAME)

        simple_definition = (
            '{"Comment": "An example of the Amazon States Language using a choice state.",'
            '"StartAt": "DefaultState",'
            '"States": '
            '{"DefaultState": {"Type": "Fail","Error": "DefaultStateError","Cause": "No Matches!"}}}'
        )

        role = "arn:aws:iam::" + ACCOUNT_ID + ":role/unknown_sf_role"

        response = client.create_state_machine(
            name="js_sf_test", definition=str(simple_definition), roleArn=role
        )

        yield client, response
