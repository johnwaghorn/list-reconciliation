import json
import os
from datetime import datetime

import boto3
import pytest
from database import Demographics, DemographicsDifferences, Jobs, JobStats
from lr_15_process_demo_diffs.lr_15_lambda_handler import DemographicDifferences
from moto import mock_dynamodb2, mock_s3, mock_ssm

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "..", "_data", "unit")

AWS_REGION = os.getenv("AWS_REGION")
MESH_BUCKET = os.getenv("MESH_BUCKET")
LR_13_REGISTRATIONS_OUTPUT_BUCKET = os.getenv("LR_13_REGISTRATIONS_OUTPUT_BUCKET")
MESH_SSM_PREFIX = os.getenv("MESH_SSM_PREFIX")


@pytest.fixture
def lambda_handler(ssm, mesh_ssm):
    app = DemographicDifferences()
    return app


PATIENTS = [
    Demographics(
        Id="c7c8b6e2-8ce2-4bc6-804e-3d7ac4054bd1",
        JobId="7b207bdb-2937-4e17-a1a9-57a2bbf3e358",
        NhsNumber="1234567890",
        IsComparisonCompleted=True,
        GP_GpPracticeCode="Y123452",
        GP_HaCipher="LNA",
        GP_TransactionDate="20200406",
        GP_TransactionTime="1340",
        GP_TransactionId="1557490",
        GP_Surname="JONES",
        GP_PreviousSurname="",
        GP_Forenames="JOHN",
        GP_Title="MR",
        GP_Gender="1",
        GP_DateOfBirth="20020101",
        GP_AddressLine1="FLAT A",
        GP_AddressLine2="THE STREET",
        GP_AddressLine3="",
        GP_AddressLine4="EAST",
        GP_AddressLine5="",
        GP_PostCode="E1   1AA",
        GP_DrugsDispensedMarker=False,
        GP_RegistrationStatus="Matched",
        PDS_GpPracticeCode="Y123452",
        PDS_GpRegisteredDate="2012-05-22",
        PDS_Surname="JOHNSON",
        PDS_Forenames=["JOHN"],
        PDS_Titles=["MR"],
        PDS_Gender="male",
        PDS_DateOfBirth="2002-02-01",
        PDS_Sensitive="U",
        PDS_Address=["FLAT A", "THE STREET", "EAST"],
        PDS_PostCode="E1   1ZZ",
        PDS_Version="1",
    ),
    Demographics(
        Id="6601b649-aeac-45b7-b0b1-8f349694008d",
        JobId="7b207bdb-2937-4e17-a1a9-57a2bbf3e358",
        NhsNumber="1234567891",
        GP_GpPracticeCode="Y123452",
        GP_HaCipher="LNA",
        GP_TransactionDate="20200406",
        GP_TransactionTime="1340",
        GP_TransactionId="1557491",
    ),
]

DIFFERENCES = [
    DemographicsDifferences(
        Id="2cc83929-4c9f-491e-b9b7-abebc338082f",
        JobId="7b207bdb-2937-4e17-a1a9-57a2bbf3e358",
        PatientId="c7c8b6e2-8ce2-4bc6-804e-3d7ac4054bd1",
        RuleId="MN-BR-SN-01",
    ),
    DemographicsDifferences(
        Id="17f15fee-b486-4ae2-8d96-4808bc47e6be",
        JobId="7b207bdb-2937-4e17-a1a9-57a2bbf3e358",
        PatientId="c7c8b6e2-8ce2-4bc6-804e-3d7ac4054bd1",
        RuleId="MN-BR-DB-01",
    ),
    DemographicsDifferences(
        Id="a07c0190-5d4c-4c7e-8bd0-a242fd565216",
        JobId="7b207bdb-2937-4e17-a1a9-57a2bbf3e358",
        PatientId="c7c8b6e2-8ce2-4bc6-804e-3d7ac4054bd1",
        RuleId="MN-BR-AD-02",
    ),
]


@pytest.fixture
def dynamodb():
    with mock_dynamodb2():
        Demographics.create_table()
        DemographicsDifferences.create_table()
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
def demographics_differences(dynamodb):
    with DemographicsDifferences.batch_write() as batch:
        for data in DIFFERENCES:
            batch.save(data)
    yield


@pytest.fixture
def jobstats(dynamodb):
    JobStats("7b207bdb-2937-4e17-a1a9-57a2bbf3e358", TotalRecords=1).save()
    yield


@pytest.fixture
def jobs(dynamodb):
    job = Jobs(
        "7b207bdb-2937-4e17-a1a9-57a2bbf3e358",
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
            Bucket=MESH_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )
        s3.create_bucket(
            Bucket=LR_13_REGISTRATIONS_OUTPUT_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )


@pytest.fixture
def ssm():
    with mock_ssm():
        yield boto3.client("ssm", region_name=AWS_REGION)


@pytest.fixture
def mesh_ssm(ssm):
    mappings = json.dumps(
        [
            {
                "id": "X26OT178TEST",
                "outbound_mappings": [
                    {
                        "dest_mailbox": "INTERNALSPINE",
                        "workflow_id": "LISTRECONCILIATIONWORKITEM-Data",
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
        Name=f"{MESH_SSM_PREFIX}/listrec_spinedsa_workflow",
        Value="LISTRECONCILIATIONWORKITEM-Data",
        Type="String",
        Overwrite=True,
    )
    yield
