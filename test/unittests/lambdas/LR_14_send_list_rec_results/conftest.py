from datetime import datetime

import json
import os

from moto import mock_s3, mock_dynamodb2, mock_ssm

import boto3
import pytest


from lambda_code.LR_14_send_list_rec_results.lr_14_lambda_handler import SendListRecResults
from utils.database.models import DemographicsDifferences, Jobs, JobStats

REGION_NAME = os.environ.get("AWS_REGION")
MESH_BUCKET = os.getenv("MESH_BUCKET")
LR_13_REGISTRATIONS_OUTPUT_BUCKET = os.getenv("LR_13_REGISTRATIONS_OUTPUT_BUCKET")
MESH_SSM_PREFIX = os.getenv("MESH_SSM_PREFIX")
EMAIL_SSM_PREFIX = os.getenv("EMAIL_SSM_PREFIX")
LISTREC_EMAIL_PASSWORD = os.getenv("LISTREC_EMAIL_PASSWORD")

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")


@pytest.fixture
def s3():
    with mock_s3():
        client = boto3.client("s3")
        client.create_bucket(
            Bucket=MESH_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
        )
        client.create_bucket(
            Bucket=LR_13_REGISTRATIONS_OUTPUT_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
        )

        client.upload_file(
            os.path.join(DATA, "pds_api_data.csv"),
            LR_13_REGISTRATIONS_OUTPUT_BUCKET,
            "7b207bdb-2937-4e17-a1a9-57a2bbf3e358/gponly.csv",
        )
        client.upload_file(
            os.path.join(DATA, "pds_api_data.csv"),
            LR_13_REGISTRATIONS_OUTPUT_BUCKET,
            "7b207bdb-2937-4e17-a1a9-57a2bbf3e358/pdsonly.csv",
        )
        client.upload_file(
            os.path.join(DATA, "pds_api_data.csv"),
            LR_13_REGISTRATIONS_OUTPUT_BUCKET,
            "7b207bdb-2937-4e17-a1a9-57a2bbf3e358/cdd.csv",
        )
        yield


@pytest.fixture
def lambda_handler(ssm, mesh_ssm, email_ssm, mock_email):
    app = SendListRecResults()
    return app


@pytest.fixture
def dynamodb():
    with mock_dynamodb2():
        DemographicsDifferences.create_table()
        Jobs.create_table()
        JobStats.create_table()
        yield


@pytest.fixture
def jobstats(dynamodb):
    JobStats(
        "7b207bdb-2937-4e17-a1a9-57a2bbf3e358",
        OnlyOnPdsRecords=3,
        OnlyOnGpRecords=5,
        PdsUpdatedRecords=0,
        HumanValidationRecords=3,
    ).save()
    yield


@pytest.fixture
def jobs(dynamodb):
    Jobs(
        "7b207bdb-2937-4e17-a1a9-57a2bbf3e358",
        PracticeCode="Y123452",
        FileName="Y123452.E1A",
        StatusId="1",
        Timestamp=datetime(2021, 5, 27, 14, 48, 37),
    ).save()
    yield


@pytest.fixture
def demographicsdifferences(dynamodb):
    DemographicsDifferences(
        Id="2cc83929-4c9f-491e-b9b7-abebc338082f",
        JobId="7b207bdb-2937-4e17-a1a9-57a2bbf3e358",
        PatientId="c7c8b6e2-8ce2-4bc6-804e-3d7ac4054bd1",
        RuleId="MN-BR-SN-01",
    ).save()
    DemographicsDifferences(
        Id="17f15fee-b486-4ae2-8d96-4808bc47e6be",
        JobId="7b207bdb-2937-4e17-a1a9-57a2bbf3e358",
        PatientId="c7c8b6e2-8ce2-4bc6-804e-3d7ac4054bd1",
        RuleId="MN-BR-DB-01",
    ).save()
    DemographicsDifferences(
        Id="a07c0190-5d4c-4c7e-8bd0-a242fd565216",
        JobId="7b207bdb-2937-4e17-a1a9-57a2bbf3e358",
        PatientId="c7c8b6e2-8ce2-4bc6-804e-3d7ac4054bd1",
        RuleId="MN-BR-AD-02",
    ).save()
    yield


@pytest.fixture
def ssm():
    with mock_ssm():
        yield boto3.client("ssm", region_name=REGION_NAME)


@pytest.fixture
def mesh_ssm(ssm):
    mappings = json.dumps(
        [
            {
                "id": "X26OT181TEST",
                "outbound_mappings": [
                    {
                        "dest_mailbox": "X26OT188TEST",
                        "workflow_id": "RSLISTRECONCILIATIONPCSE",
                    }
                ],
            }
        ]
    )
    ssm.put_parameter(
        Name=f"{MESH_SSM_PREFIX}/mesh_mappings",
        Value=mappings,
        Type="String",
        Overwrite=True,
    )
    ssm.put_parameter(
        Name=f"{MESH_SSM_PREFIX}/listrec_pcse_workflow",
        Value="RSLISTRECONCILIATIONPCSE",
        Type="String",
        Overwrite=True,
    )
    yield


@pytest.fixture
def email_ssm(ssm):
    ssm.put_parameter(
        Name=f"{EMAIL_SSM_PREFIX}/list_rec_email_password",
        Value=LISTREC_EMAIL_PASSWORD,
        Type="SecureString",
        Overwrite=True,
    )
    yield
