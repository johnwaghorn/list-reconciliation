import os

import boto3
import pytest
from database.models import InFlight, Jobs
from dateutil.parser import parse
from jobs.statuses import JobStatus
from lr_27_job_cleanup.lr_27_lambda_handler import JobCleanup
from moto import mock_dynamodb2, mock_s3

REGION_NAME = os.environ.get("AWS_REGION")

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "..", "_data", "lr-13")

JOB_ID = "00000000-0000-0000-0000-000000000000"
PRACTICE_CODE = "A82023"
DATA_FILE = "A82023_GPR4LNA1.CSA"
CCD_DATA_FILE = "A82023-CDD-19700101000000.csv"
GP_DATA_FILE = "A82023-OnlyOnGP-19700101000000.csv"
PDS_DATA_FILE = "A82023-OnlyOnPDS-19700101000000.csv"
MOCK_REGISTRATIONS_OUTPUT_BUCKET = os.environ.get("LR_13_REGISTRATIONS_OUTPUT_BUCKET")


@pytest.fixture
def job_cleanup(create_output_bucket, create_dynamodb_tables):
    return JobCleanup()


@pytest.fixture
def create_dynamodb_tables(dynamodb):
    Jobs.create_table()
    InFlight.create_table()
    yield


@pytest.fixture
def create_output_bucket(s3):
    s3.create_bucket(
        Bucket=MOCK_REGISTRATIONS_OUTPUT_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
    )


@pytest.fixture
def upload_registration_outputs_to_s3(s3, create_output_bucket):
    for data_file in [CCD_DATA_FILE, GP_DATA_FILE, PDS_DATA_FILE]:
        s3.upload_file(
            os.path.join(DATA, data_file),
            MOCK_REGISTRATIONS_OUTPUT_BUCKET,
            os.path.join(JOB_ID, data_file),
        )


@pytest.fixture
def create_job_item(dynamodb):
    job = Jobs(
        JOB_ID,
        PracticeCode=PRACTICE_CODE,
        FileName=DATA_FILE,
        StatusId=JobStatus.COMPLETE.value,
        Timestamp=parse("1970-01-01 00:00:00.000000"),
    )
    job.save()


@pytest.fixture
def create_inflight_item(dynamodb):
    inflight = InFlight(JOB_ID, TotalRecords=1)
    inflight.save()


@pytest.fixture(scope="function")
def dynamodb():
    with mock_dynamodb2():
        yield boto3.client("dynamodb", region_name=REGION_NAME)


@pytest.fixture(scope="function")
def s3():
    with mock_s3():
        yield boto3.client("s3", region_name=REGION_NAME)
