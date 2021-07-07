import boto3
import pytest
from dateutil.parser import parse
from moto import mock_dynamodb2, mock_stepfunctions
from moto.core import ACCOUNT_ID

from lambda_code.LR_09_scheduled_check.LR09_lambda_handler import ScheduledCheck
from utils.database.models import Demographics, InFlight, Jobs, JobStats

JOB_ID = "b204b5f4-6762-414e-bb6b-a05c37f52956"
JOB_ID_2 = "3af674be-1e7f-470c-b6d1-ca5ce6d9c600"
JOB_ID_3 = "87e36ab6-4f25-4c47-9e13-d029f1e4c925"
REGION_NAME = "eu-west-2"


@pytest.fixture(autouse=True)
def lambda_handler():
    app = ScheduledCheck()
    return app


FAKE_PATIENTS = [
    Demographics(
        Id="d2305c19-96b3-4e81-91af-d26f2281b67f",
        JobId=JOB_ID,
        NhsNumber="111",
        IsComparisonCompleted=True,
        GP_GpCode="JSABCDEF",
        PDS_GpCode="JSABCDEF",
        GP_HaCipher="123",
        GP_TransactionDate="1",
        GP_TransactionTime="1",
        GP_TransactionId="1",
    ),
    Demographics(
        Id="29263475-1c38-4d2e-a477-0004ba9f04b2",
        JobId=JOB_ID,
        NhsNumber="222",
        IsComparisonCompleted=True,
        GP_GpCode="JSABCDEF",
        PDS_GpCode="JSABCDEF",
        GP_HaCipher="123",
        GP_TransactionDate="1",
        GP_TransactionTime="1",
        GP_TransactionId="1",
    ),
    Demographics(
        Id="6cea6924-1ed9-423e-a69f-6d868f58b278",
        JobId=JOB_ID,
        NhsNumber="333",
        IsComparisonCompleted=True,
        GP_GpCode="JSABCDEF",
        PDS_GpCode="JSABCDEF",
        GP_HaCipher="123",
        GP_TransactionDate="1",
        GP_TransactionTime="1",
        GP_TransactionId="1",
    ),
    Demographics(
        Id="50e1b957-2fc4-44b0-8e60-d8f9ca162022",
        JobId=JOB_ID,
        NhsNumber="444",
        IsComparisonCompleted=True,
        GP_GpCode="JSABCDEF",
        PDS_GpCode="JSABCDEF",
        GP_HaCipher="123",
        GP_TransactionDate="1",
        GP_TransactionTime="1",
        GP_TransactionId="1",
    ),
    Demographics(
        Id="78490ae9-4908-4414-bf83-6b5452f18644",
        JobId=JOB_ID,
        NhsNumber="555",
        IsComparisonCompleted=True,
        GP_GpCode="JSABCDEF",
        PDS_GpCode="JSGHIJKLM",
        GP_HaCipher="123",
        GP_TransactionDate="1",
        GP_TransactionTime="1",
        GP_TransactionId="1",
    ),
    Demographics(
        Id="3af674be-1e7f-470c-b6d1-ca5ce6d9c600",
        JobId=JOB_ID,
        NhsNumber="666",
        IsComparisonCompleted=True,
        GP_GpCode="JSABCDEF",
        PDS_GpCode="JSGHIJKLM",
        GP_HaCipher="123",
        GP_TransactionDate="1",
        GP_TransactionTime="1",
        GP_TransactionId="1",
    ),
    Demographics(
        Id="3af674be-1e7f-470c-b6d1-ca5ce6d9c601",
        JobId=JOB_ID_3,
        NhsNumber="777",
        IsComparisonCompleted=False,
        GP_GpCode="JSABCDEG",
        PDS_GpCode="JSGHIJKLN",
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
        InFlight(JOB_ID, TotalRecords=6),
        InFlight(JOB_ID_2, TotalRecords=1),
        InFlight(JOB_ID_3, TotalRecords=1),
    ]

    with InFlight.batch_write() as batch:
        for item in items:
            batch.save(item)

    yield


@pytest.fixture
def populate_jobs_table(create_dynamo_tables):
    job = Jobs(
        JOB_ID,
        PracticeCode="JSABCDEF",
        FileName="JSHTST.EAA",
        StatusId="1",
        Timestamp=parse("2021-05-27 14:48:37.274977"),
    )

    job.save()
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
